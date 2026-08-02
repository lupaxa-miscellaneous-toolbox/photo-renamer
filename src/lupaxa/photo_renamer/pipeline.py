"""End-to-end media rename planning and execution."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import AbstractContextManager, nullcontext
from pathlib import Path

from rich.console import Console
from rich.progress import Progress

from lupaxa.photo_renamer.collisions import ensure_unique
from lupaxa.photo_renamer.config import AppConfig
from lupaxa.photo_renamer.metadata import extract_timestamp
from lupaxa.photo_renamer.models import MediaFile, RenamePlan, RunStats, TimestampResult
from lupaxa.photo_renamer.organiser import resolve_destination_dir
from lupaxa.photo_renamer.progress import make_progress
from lupaxa.photo_renamer.rename import apply_plan, build_filename, is_already_named
from lupaxa.photo_renamer.reporting import LogWriter, print_startup, print_summary
from lupaxa.photo_renamer.scanner import ScanError, scan_media
from lupaxa.photo_renamer.source_detection import detect_source

_MISSING_METADATA = "metadata missing"
_ALREADY_NAMED = "already named"


def _plan_file(
    media: MediaFile,
    config: AppConfig,
    reserved: set[Path],
) -> tuple[RenamePlan, bool]:
    detected_source = detect_source(media.path.name)
    if config.skip_existing and not config.force and is_already_named(media.path.name):
        timestamp = TimestampResult(value=None, origin="none", missing=False)
        return (
            RenamePlan(
                source=media.path,
                destination=media.path,
                detected_source=detected_source,
                timestamp=timestamp,
                action="skip",
                skipped_reason=_ALREADY_NAMED,
            ),
            False,
        )

    timestamp = extract_timestamp(media.path, config.timestamp_mode, config.timezone)
    if timestamp.missing or timestamp.value is None:
        return (
            RenamePlan(
                source=media.path,
                destination=media.path,
                detected_source=detected_source,
                timestamp=timestamp,
                action="skip",
                skipped_reason=_MISSING_METADATA,
            ),
            False,
        )

    filename = build_filename(
        timestamp.value,
        media.extension,
        config.name_format,
        detected_source,
    )
    destination_dir = resolve_destination_dir(
        root=config.root,
        output_dir=config.output_dir,
        source_file=media.path,
        detected_source=detected_source,
        organise=config.organise,
        flatten=config.flatten,
    )
    destination, collided = ensure_unique(destination_dir / filename, reserved=reserved)
    destination = destination.resolve()
    reserved.add(destination)
    return (
        RenamePlan(
            source=media.path,
            destination=destination,
            detected_source=detected_source,
            timestamp=timestamp,
            action="move" if config.move else "copy",
            skipped_reason=None,
        ),
        collided,
    )


def plan_file(media: MediaFile, config: AppConfig, reserved: set[Path]) -> RenamePlan:
    """Build a collision-safe rename plan and reserve its resolved destination."""
    plan, _ = _plan_file(media, config, reserved)
    return plan


def _write_log(writer: LogWriter | None, plan: RenamePlan, message: str = "") -> None:
    if writer is None:
        return
    writer.write_event(
        action=plan.action,
        source=plan.source,
        destination=None if plan.action == "skip" else plan.destination,
        source_label=plan.detected_source,
        origin=plan.timestamp.origin,
        message=message,
    )


def _show_verbose(console: Console, config: AppConfig, plan: RenamePlan, message: str) -> None:
    if not config.verbose or config.quiet:
        return
    if plan.action == "skip":
        console.print(f"[yellow]skip[/yellow] {plan.source}: {message}")
    else:
        console.print(f"{plan.action} {plan.source} -> {plan.destination}{message}")


def _progress_context(
    console: Console,
    config: AppConfig,
    total: int,
    description: str,
) -> AbstractContextManager[Progress | None]:
    if config.quiet:
        return nullcontext(None)
    return make_progress(console, total, description)


def _log_failure(
    writer: LogWriter | None,
    console: Console,
    config: AppConfig,
    plan: RenamePlan,
    exc: Exception,
) -> None:
    if writer is not None:
        writer.write_event(
            action="failed",
            source=plan.source,
            destination=plan.destination,
            source_label=plan.detected_source,
            origin=plan.timestamp.origin,
            message=str(exc),
        )
    if config.verbose and not config.quiet:
        console.print(f"[red]failed[/red] {plan.source}: {exc}")


def _log_context(config: AppConfig) -> AbstractContextManager[LogWriter | None]:
    if config.log_file is None or config.dry_run:
        return nullcontext(None)
    return LogWriter(config.log_file)


def run(config: AppConfig, console: Console | None = None) -> RunStats:
    """Scan, plan, and execute a configured photo rename run."""
    console = console or Console(quiet=config.quiet)
    scan_errors: list[ScanError] = []
    media_files = scan_media(
        config.root,
        recursive=config.recursive,
        output_dir=config.output_dir,
        include=config.include,
        exclude=config.exclude,
        errors=scan_errors,
    )
    stats = RunStats(scanned=len(media_files), failed=len(scan_errors))
    reserved: set[Path] = set()
    print_startup(console, config, len(media_files))
    if config.verbose and not config.quiet:
        for scan_error in scan_errors:
            console.print(f"[red]failed[/red] {scan_error.path}: {scan_error.message}")

    actionable: list[RenamePlan] = []
    with _log_context(config) as writer:
        with _progress_context(console, config, len(media_files), "Planning media") as progress:
            task_id = progress.task_ids[0] if progress is not None else None
            for media in media_files:
                plan: RenamePlan | None = None
                try:
                    plan, collided = _plan_file(media, config, reserved)
                    if collided:
                        stats.collisions += 1

                    if plan.skipped_reason == _MISSING_METADATA:
                        stats.failed += 1
                        stats.metadata_missing += 1
                        _write_log(writer, plan, _MISSING_METADATA)
                        _show_verbose(console, config, plan, _MISSING_METADATA)
                    elif plan.action == "skip":
                        stats.skipped += 1
                        reason = plan.skipped_reason or "skipped"
                        _write_log(writer, plan, reason)
                        _show_verbose(console, config, plan, reason)
                    else:
                        actionable.append(plan)
                except OSError as exc:
                    stats.failed += 1
                    if writer is not None:
                        writer.write_event(
                            action="failed",
                            source=media.path,
                            destination=plan.destination if plan is not None else None,
                            source_label=(
                                plan.detected_source
                                if plan is not None
                                else detect_source(media.path.name)
                            ),
                            origin=plan.timestamp.origin if plan is not None else "none",
                            message=str(exc),
                        )
                    if config.verbose and not config.quiet:
                        console.print(f"[red]failed[/red] {media.path}: {exc}")
                finally:
                    if progress is not None and task_id is not None:
                        progress.advance(task_id)

        apply_description = (
            "Dry-run apply"
            if config.dry_run
            else ("Moving media" if config.move else "Copying media")
        )
        with _progress_context(console, config, len(actionable), apply_description) as progress:
            task_id = progress.task_ids[0] if progress is not None else None

            def _apply(plan: RenamePlan) -> RenamePlan:
                apply_plan(plan, dry_run=config.dry_run)
                return plan

            with ThreadPoolExecutor(max_workers=config.workers) as executor:
                futures = {executor.submit(_apply, plan): plan for plan in actionable}
                for future in as_completed(futures):
                    plan = futures[future]
                    try:
                        future.result()
                    except OSError as exc:
                        stats.failed += 1
                        _log_failure(writer, console, config, plan, exc)
                    except Exception as exc:  # noqa: BLE001 - surface unexpected worker errors
                        stats.failed += 1
                        _log_failure(writer, console, config, plan, exc)
                    else:
                        stats.processed += 1
                        message = " (dry-run)" if config.dry_run else ""
                        _write_log(writer, plan, message.strip())
                        _show_verbose(console, config, plan, message)
                    finally:
                        if progress is not None and task_id is not None:
                            progress.advance(task_id)

    if not config.quiet:
        print_summary(console, stats)
    return stats

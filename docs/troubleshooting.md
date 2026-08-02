# Troubleshooting and FAQ

## No files are scanned

- Add `--recursive` if media is below nested directories.
- Check that extensions are supported and that `--include` or `--exclude` is not filtering them.
- Files inside the resolved output directory are intentionally ignored.
- Symlinked directories and files are not followed.

## Missing metadata is reported

`--timestamp exif` requires an embedded image EXIF or video MediaInfo date. Use
`--timestamp auto` to permit filesystem fallback, or `--timestamp filesystem` to always use
modification time.

## Video timestamps are unavailable

Install the MediaInfo system package. If MediaInfo cannot read a date, `auto` mode falls back
to filesystem modification time. Corrupt or unsupported embedded data is handled per file.

## Times are unexpected

Use `--verbose` and `--log-file` to inspect each timestamp origin. Pass an IANA timezone:

```bash
photo-renamer --timezone Europe/London --dry-run PATH
```

Naive embedded timestamps do not identify their original zone; when a zone is supplied they
are interpreted in that zone.

## A `_001` suffix appears

The desired destination already existed or was reserved by an earlier file in the same run.
Suffixing is intentional and prevents overwrites. Existing files are never replaced.

## Permission or path errors

Verify read access to input files and write access to the output parent. Shorten the output path
if the operating system rejects a long filename. Per-file I/O failures do not stop later files,
but the process exits with status `1`.

## FAQ

### Are originals preserved?

Yes, by default. The tool copies files. Only `--move` removes successfully processed sources.

### Does `--preserve-source` preserve originals?

No; originals are already preserved by copy mode. This option is a naming alias for
`--format source`, adding labels such as `WhatsApp` to filenames.

### Can it overwrite a file?

No. It chooses a unique suffixed name and also uses exclusive destination creation to protect
against races.

### Does it modify EXIF or video metadata?

No. Metadata and media content are read but never rewritten.

### Can it detect duplicate content?

No. Collision handling is based on destination names, not hashes or visual similarity.

### Is there an undo command?

Not in v1. Preview with `--dry-run`, keep copy mode when possible, and use `--log-file` for an
audit trail that records original and destination paths.

### What happens to unrecognised source names?

They receive the `Unknown` label when source labels are included in names or directories.

### Why was an already formatted file processed?

Already formatted names are only skipped when `--skip-existing` is supplied. `--force`
overrides that skip when both flags are present.

# Examples

## Preview, then copy

```bash
photo-renamer --dry-run --recursive ~/Pictures
photo-renamer --recursive ~/Pictures
```

The second command copies results to `~/Pictures/renamed/` and leaves originals in place.

## Move into an archive

```bash
photo-renamer --dry-run --recursive --move --output /Volumes/Archive ~/Pictures
photo-renamer --recursive --move --output /Volumes/Archive ~/Pictures
```

Only use the second command after reviewing the preview. Successfully processed sources are
removed in move mode.

## Include source in names

```bash
photo-renamer --recursive --format source ~/Pictures
```

```text
IMG-20260801-WA0001.JPG
→ 2026-08-01_14-55-22_WhatsApp.jpg
```

Put the label first with `--format source-first`, or use `--preserve-source` as shorthand for
`--format source`.

## Organise while preserving directories

For `holiday/day-1/IMG-20260801-WA0001.JPG`:

```bash
photo-renamer --recursive --organise ~/Pictures
```

```text
renamed/holiday/day-1/WhatsApp/2026-08-01_14-55-22.jpg
```

The detected source directory is nested **inside** the preserved relative path.

## Flatten output

```bash
photo-renamer --recursive --flatten ~/Pictures
# renamed/2026-08-01_14-55-22.jpg

photo-renamer --recursive --flatten --organise ~/Pictures
# renamed/WhatsApp/2026-08-01_14-55-22.jpg
```

Filename collisions are safely suffixed even when files from many directories converge.

## Filter formats and choose timestamps

```bash
photo-renamer --recursive --include jpg,jpeg,heic --timestamp filesystem ~/Pictures
```

This limits processing to the listed supported image types and always uses modification time.

## Convert to a target timezone

```bash
photo-renamer --recursive --timezone Europe/London ~/Pictures
```

Use a valid IANA timezone identifier.

## Keep an audit log

```bash
photo-renamer --recursive --log-file ./rename-events.tsv ~/Pictures
```

The append-only tab-separated log records event time, action, source, destination, detected
source label, timestamp origin, and a message.

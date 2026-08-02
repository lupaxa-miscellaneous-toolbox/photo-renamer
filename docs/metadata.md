# Metadata and timestamps

Every output filename begins or ends with a resolved timestamp formatted as
`YYYY-MM-DD_HH-MM-SS`.

## Image priority

Images are inspected with Pillow and pillow-heif. Embedded fields are tried in this order:

1. EXIF `DateTimeOriginal`
2. EXIF `DateTimeDigitized`
3. EXIF `DateTime`
4. filesystem modification time, when the selected mode allows fallback

The supported image formats are JPG, JPEG, PNG, HEIC, HEIF, WebP, TIF, and TIFF. A format being
supported does not guarantee that a particular file contains EXIF metadata.

## Video priority

Videos are inspected through MediaInfo. Common recorded, creation, encoded, and tagged date
fields are tried before filesystem modification time. Install the MediaInfo system package as
well as the Python dependency for embedded video timestamps.

The supported video formats are MP4, MOV, AVI, MKV, M4V, and 3GP.

## Timestamp modes

### `auto` (default)

Use embedded image or video metadata when available, otherwise use filesystem modification
time.

### `exif`

Use embedded metadata only. Despite the familiar option name, this means EXIF for images and
MediaInfo dates for videos. A file with no usable embedded timestamp is reported as missing
metadata, skipped, and counted as a failure.

### `filesystem`

Always use filesystem modification time; embedded metadata is not inspected for naming.

## Timezones

`--timezone ZONE` accepts an IANA identifier such as `Europe/London` or `America/New_York`.
Aware timestamps are converted into the requested zone. Naive embedded timestamps are
interpreted in that zone, and the resulting wall-clock components are used in the filename.

Without `--timezone`, embedded values retain their extracted wall-clock representation and
filesystem modification time uses the host's local timezone.

## Metadata is not modified

The tool reads metadata only. Copying preserves file timestamps and metadata; moving relocates
the file. Neither operation rewrites EXIF, video tags, or media content.

# Source detection

Source detection uses the original filename. Rules are case-insensitive and the first matching
rule wins.

| Label | Recognised filename beginnings or patterns |
| --- | --- |
| WhatsApp | `IMG-...-WA...`, `VID-...-WA...` |
| Telegram | `Photo_...`, `Video_...` |
| Signal | `signal-...`, or a name ending with `_signal` before its extension |
| Pixel | `PXL_...` |
| Samsung | eight digits followed by `_`, such as `20260801_...` |
| iPhone | `IMG_` followed by four digits |
| Screenshot | `Screenshot...`, `Screen Shot...`, `Screen_...` |
| Camera | `DSC_...`, `DSCF...` |
| Unknown | any filename not matched above |

Detection does not inspect image pixels, metadata maker fields, or application databases.
Renaming an input before processing can therefore change or remove a match.

## Using the label

The default `datetime` format detects the source internally but does not include it in the
filename. Use:

```bash
photo-renamer --format source PATH
# 2026-08-01_14-55-22_WhatsApp.jpg

photo-renamer --format source-first PATH
# WhatsApp_2026-08-01_14-55-22.jpg
```

`--preserve-source` is an alias for `--format source`.

Use `--organise` to create a detected-source directory. Unmatched files use `Unknown`:

```text
renamed/holiday/Unknown/2026-08-01_14-55-22.jpg
```

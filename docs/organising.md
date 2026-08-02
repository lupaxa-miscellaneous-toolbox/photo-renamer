# Organising media

The destination root defaults to `renamed` below the source `PATH`. A relative `--output` is
also resolved below `PATH`; an absolute output is used as given.

Assume this input:

```text
PATH/vacation/day-1/IMG-20260801-WA0001.jpg
```

## Preserve relative paths (default)

With `--recursive`, relative directories are preserved:

```text
PATH/renamed/vacation/day-1/2026-08-01_14-55-22.jpg
```

## Group by source

`--organise` appends the detected source directory **inside** the preserved relative path:

```text
PATH/renamed/vacation/day-1/WhatsApp/2026-08-01_14-55-22.jpg
```

It does not put `WhatsApp` before `vacation/day-1`.

## Flatten

`--flatten` drops all relative input directories:

```text
PATH/renamed/2026-08-01_14-55-22.jpg
```

Combining both options keeps only the detected source directory:

```text
PATH/renamed/WhatsApp/2026-08-01_14-55-22.jpg
```

| Options | Destination below output |
| --- | --- |
| none | `vacation/day-1/2026-08-01_14-55-22.jpg` |
| `--organise` | `vacation/day-1/WhatsApp/2026-08-01_14-55-22.jpg` |
| `--flatten` | `2026-08-01_14-55-22.jpg` |
| `--flatten --organise` | `WhatsApp/2026-08-01_14-55-22.jpg` |

## Collisions and output scans

Flattening can bring unrelated files to the same destination. No file is overwritten:
collisions become `_001`, `_002`, and so on. The entire resolved output tree is excluded from
scanning, so recursive runs do not process earlier output.

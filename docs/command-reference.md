# Command reference

```text
photo-renamer [options] PATH
```

`PATH` is the directory to scan.

| Option | Default | Behaviour |
| --- | --- | --- |
| `--output DIR` | `renamed` | Destination root; relative paths resolve below `PATH` |
| `--recursive` | off | Search subdirectories |
| `--dry-run` | off | Plan and report without copying, moving, creating directories, or logging |
| `--verbose` | off | Print per-file actions and failures |
| `--quiet` | off | Suppress startup, progress, summary, and verbose output |
| `--force` | off | Process already named files when `--skip-existing` is also set |
| `--skip-existing` | off | Skip files matching a generated date-based name |
| `--timestamp MODE` | `auto` | `auto`, `exif`, or `filesystem` |
| `--format FORMAT` | `datetime` | `datetime`, `source`, or `source-first` |
| `--preserve-source` | off | Alias for `--format source`; explicit `--format` wins |
| `--organise` | off | Append detected source beneath the preserved relative directory |
| `--flatten` | off | Remove relative source directories from output paths |
| `--move` | off | Move instead of copy |
| `--include EXT,...` | all supported | Include only listed supported extensions |
| `--exclude EXT,...` | none | Exclude listed extensions |
| `--timezone ZONE` | unset | Convert timestamps to an IANA zone before formatting |
| `--log-file PATH` | unset | Append tab-separated audit events on real runs |

## Exit codes

- `0`: every scanned file succeeded or was intentionally skipped.
- `1`: at least one file failed, including missing metadata in `exif` mode.
- `2`: invalid CLI configuration, such as an unknown timezone or combining `--quiet` and
  `--verbose`.

## Safety guarantees

Copy is the default. Destination paths are opened exclusively and are never overwritten. If a
name is taken, `_001`, `_002`, and subsequent suffixes are added before the extension. The
resolved output tree is excluded from scans.

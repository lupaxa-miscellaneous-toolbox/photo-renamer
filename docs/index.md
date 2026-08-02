# lupaxa-photo-renamer

`lupaxa-photo-renamer` is a Python CLI for safely copying or moving photographs and videos
into consistent, date-based filenames.

It can:

- read image EXIF and video creation metadata;
- fall back to filesystem modification time;
- detect common source apps and devices from filenames;
- preserve relative directories or flatten output;
- group files by detected source;
- prevent overwrites with deterministic collision suffixes; and
- show startup, progress, and summary output with Rich.

> **Screenshot placeholder:** a capture of the Rich startup panel, progress bar, and summary
> will be added under `docs/assets/`.

## Safe defaults

The defaults are deliberately conservative:

- files are **copied**, not moved;
- output goes to `PATH/renamed/`;
- relative directory structure is preserved;
- recursion is off until `--recursive` is supplied;
- existing destinations are never overwritten.

Start with a preview:

```bash
photo-renamer --dry-run --recursive ~/Pictures
```

Continue with [installation](installation.md), then read the [usage guide](usage.md) or jump
to the [examples](examples.md).

The project is distributed under the MIT License in the repository's `LICENCE` file.

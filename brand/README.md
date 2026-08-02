# Brand assets

Source artwork and derived logos for Photo Renamer.

## Palette

| Token | Hex       |
| ----- | --------- |
| Navy  | `#203959` |
| Ink   | `#FFFFFF` |

## Sources

| File                          | Purpose                                        |
| ----------------------------- | ---------------------------------------------- |
| `source/mark.png`             | Square mark (photo frame + calendar)           |
| `source/mark-transparent.png` | White mark, transparent background             |
| `source/social.png`           | Wide lockup with wordmark                      |
| `source/icon-1024.png`        | Navy-padded square used for favicon generation |

## Derived outputs

| File                                      | Size         | Used by                            |
| ----------------------------------------- | ------------ | ---------------------------------- |
| `readme-logo.png`                         | 1280×320     | GitHub README header               |
| `../mkdocs/assets/images/logo.png`        | 256×256 RGBA | MkDocs header logo (transparent)   |
| `../mkdocs/assets/images/favicon.png`     | 128×128      | MkDocs / browser favicon           |
| `../mkdocs/assets/images/social-card.png` | 1200×630     | Open Graph / social preview        |
| `../mkdocs/assets/images/favicons/`       | modern set   | PWA / HTML favicon bundle          |

Regenerate the favicon bundle:

```bash
favicon-generator brand/source/icon-1024.png \
  --output-dir mkdocs/assets/images/favicons \
  --fit contain \
  --background "#203959" \
  --padding 0.06 \
  --theme-colour "#203959" \
  --background-colour "#203959" \
  --name "Photo Renamer" \
  --short-name "Photo Renamer" \
  --prefix /assets/images/favicons/ \
  --overwrite
```

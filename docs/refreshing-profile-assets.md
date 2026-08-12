# Refreshing Profile Assets

This repository uses locally generated profile visuals so the README does not depend on third-party runtime statistics services.

## Refresh command

From the repository root, run:

```bash
./scripts/refresh-assets.sh
```

The wrapper reads `data/contribution_calendar_summary.json`, which is the committed contribution snapshot captured from the live GitHub profile, and regenerates the files in `assets/`. The snapshot includes its UTC capture timestamp and the complete retrieved calendar window.

## Generated files

| File | Purpose |
|---|---|
| `assets/glow-divider.svg` | Dark-first cyan, violet, and pink section divider. |
| `assets/tech-strip.svg` | Vector technology-focus strip. |
| `assets/tech-strip.png` | Raster fallback used by the README for deterministic text rendering. |
| `assets/contribution-isometric.svg` | Vector contribution-field rendering. |
| `assets/contribution-isometric.png` | Raster contribution-field rendering used by the README. |
| `assets/profile-typing.gif` | Animated identity strip for the profile header. |

## Data integrity

The contribution visualization is intentionally modest. The current committed snapshot records **9 total contributions**, **4 active days**, and a maximum of **5 contributions on a single day** across the retrieved 368-day window. The snapshot was captured on 2026-08-12 UTC from the public GitHub profile and must not be edited to imply a stronger activity record.

The project description in the README is limited to facts documented in the private CardX Pro README. No private source code, credentials, or repository internals are copied into this public profile repository.

## Design notes

The README uses PNG fallbacks for text-bearing visuals because GitHub clients and local SVG renderers can differ in font availability. The original SVG assets remain available for reuse and inspection. The original `ai-automation-lab.png` and `ai-automation-lab-motion.gif` assets are preserved and remain part of the profile design.

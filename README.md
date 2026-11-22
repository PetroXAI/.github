# PetroXAI · `.github`

Organization profile and public visual assets for **[github.com/PetroXAI](https://github.com/PetroXAI)**.

## Structure

- [`profile/README.md`](profile/README.md) — Public organization homepage rendered on [github.com/PetroXAI](https://github.com/PetroXAI).
- `profile/assets/` — Adaptive dark/light hero banners, institutional provenance banners, and rounded product icons.
- `scripts/render_assets.py` — Reproducible headless-Chromium script for regenerating visual assets from brand vector sources.

## Regenerating Visual Assets

```bash
python3 scripts/render_assets.py \
  --brand-dir /path/to/brand \
  --font-file /path/to/saira-latin-standard-normal.woff2
```

Requires Python 3 (with `Pillow`) and a local Chromium / Chrome headless binary.

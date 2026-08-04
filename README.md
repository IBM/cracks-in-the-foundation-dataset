# Cracks in the Foundation (CiF) — Website

Static promotional site for the CiF dataset & paper, served via GitHub Pages at
`https://<username>.github.io/<repo>/`.

- Paper: https://arxiv.org/abs/2605.18413
- Dataset: https://huggingface.co/datasets/ibm-research/cif-dataset

## Structure

- `index.html`, `assets/css`, `assets/js` — plain HTML/CSS/JS, no build step, no framework.
- `assets/img/` — optimized web images (hero, gallery). Generated once from the raw source
  material in `assets/images/` (kept for provenance, not served directly by the site).
- `assets/images/` — raw source images/figures from the paper (full-resolution photos, defect
  examples, comparison figures, chart PDFs). Not linked from the site; kept as provenance and to
  regenerate `assets/img/` assets if needed.
- `scripts/update_downloads.py` — fetches HF download stats; run daily by
  `.github/workflows/update-downloads.yml`, which writes `assets/data/downloads.json`.
- `CiF_Dataset_Neurips.pdf`, `CiF.pptx` — original paper/slides, kept for reference.

## Local preview

```
python3 -m http.server 8000
```

then open http://localhost:8000/

## Updating download stats manually

Requires a Hugging Face token with access to the `ibm-research` org's publisher analytics,
stored as the `HF_TOKEN` repository secret (Settings → Secrets and variables → Actions).
Trigger manually via Actions → "Update HF download counter" → Run workflow, or wait for the
daily scheduled run.

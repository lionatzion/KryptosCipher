# RUN_GUIDE.md — Reproducing the K4 Period‑27 Sweep

## 1) Prereqs
- Python 3.8+
- No external packages required for the baseline sweep
- Optional: Jupyter to run the notebooks

## 2) Where to put files
- Place `kryptos_k4_p27_sweep.py` in the repo root (or `scripts/`).
- Ensure an output folder exists; this guide uses `out/`.

## 3) Baseline run (period 27)
From the repository root:
```bash
python kryptos_k4_p27_sweep.py --outdir ./out --topn 100
```
What this enforces:
- Islands: **EAST** (22–25), **NORTHEAST** (26–34), **BERLIN** (64–69), **CLOCK** (70–74)
- A‑enforcement: positions **33** and **74**
- Period: **27**

Expected outputs in `out/`:
- `k4_top10_summary.json`
- `k4_top100_candidates_light.csv`
- (optionally) a small run readme/provenance file

## 4) Variations
Run once for completeness (lower priority than P=27):
```bash
python kryptos_k4_p27_sweep.py --period 28 --outdir ./out/p28 --topn 100
python kryptos_k4_p27_sweep.py --period 29 --outdir ./out/p29 --topn 100
```
Turn off A‑enforcement (not recommended):
```bash
python kryptos_k4_p27_sweep.py --no-enforce-a --outdir ./out/noA
```

## 5) Notebook workflows (optional)
- `notebooks/K4_P27_Sweep.ipynb` — one‑click baseline run
- `notebooks/K4_P28_29_SanityChecks.ipynb` — one‑click completeness checks
- `notebooks/Minimal_Transposition_Probe.ipynb` — stub to test a small reversible 7×14 route
- `notebooks/Review_Top_Candidates.ipynb` — load JSON/CSV and inspect windows

## 6) Common pitfalls (Windows/Git Bash)
- **“Not a directory: data”** → you have a *file* named `data`; rename/remove it, then `mkdir -p data/exports`.
- **“adding embedded git repository”** → you accidentally put a `.git` inside the repo. Remove the nested `.git`, then `git rm -f --cached -r <that-folder>`.
- Prefer relative paths like `out/` (not `/out`) and quote any paths with spaces.

## 7) Upload to GitHub (manual)
- On GitHub: Add file → Upload files. Place JSON/CSV into `data/exports/`, notebooks into `notebooks/`, docs into `docs/`, and `README.md`/`RUN_GUIDE.md` at the root.

## 8) Re‑run checklist
- Islands still align at the same indices
- A‑enforcement at positions 33 and 74
- Period 27 baseline beats P=28/29 on function‑word bridges and overall score

_Last updated: 2025-08-26 05:58:11_

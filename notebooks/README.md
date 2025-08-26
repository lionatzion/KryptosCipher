# KryptosCipher — K4 period‑27 baseline workspace

This repository tracks a **constraint‑driven** search for a period‑27 Vigenère‑style keystream on Kryptos K4, with reproducible scripts, notebooks, and exports.

## TL;DR (quick start)
```bash
# from the repo root
python kryptos_k4_p27_sweep.py --outdir ./out --topn 100
```
Outputs will appear in `out/`:
- `k4_top10_summary.json` — top‑10 candidates with `rank`, `score`, `unknown_fill`, `keystream_27`, `plaintext`
- `k4_top100_candidates_light.csv` — top‑N lightweight table (rank, score, unknown_fill, keystream_27)

## Method in one paragraph
We model K4’s final layer as a repeating Vigenère keystream with **period 27**. We **hard‑lock the four plaintext islands** at absolute positions (1‑based) — **EAST** (22–25), **NORTHEAST** (26–34), **BERLIN** (64–69), **CLOCK** (70–74) — and **enforce zero‑shift ‘A’** at positions **33** and **74**. Those anchors determine 24/27 cycle residues; the remaining unknowns (r7, r8, r20) are exhausted over A..Z. Each full 97‑char decrypt is scored with a light English fitness (chi‑square + common bigrams + function‑word hits).

## Repository layout (suggested)
- `kryptos_k4_p27_sweep.py` — main sweep CLI
- `RUN_GUIDE.md` — step‑by‑step instructions and troubleshooting
- `notebooks/`
  - `K4_P27_Sweep.ipynb` — run baseline sweep and write `out/` artifacts
  - `K4_P28_29_SanityChecks.ipynb` — completeness checks for P=28/29
  - `Minimal_Transposition_Probe.ipynb` — (stub) reversible 7×14 route probe
  - `Review_Top_Candidates.ipynb` — inspect JSON/CSV and island windows
- `docs/`
  - `hypothesis.md` — two‑layer working model (optional tiny transposition + P=27)
  - `analysis.md` — eliminated methods and next steps
- `data/exports/` (or `out/`) — JSON/CSV artifacts and status snapshots
  - `k4_top10_summary.json`
  - `k4_top100_candidates_light.csv`
  - `kryptos_k4_conclusions.json`
  - `DEAD_ENDS.md`, `NOTES_README.md`

## Dead‑ends / de‑prioritized (keep this current)
- Raw **Berlin‑Clock lamp‑count → shift** mappings
- Unconstrained **tableau pointer walks** (even with the extra “L” row)
- Final‑layer periods **2–26**; **28/29** kept only for a one‑time check

## Contributing
- Prefer small JSON/CSV exports over large dumps.
- When an approach is ruled out, add a line to `DEAD_ENDS.md` and update `docs/analysis.md`.
- Use clear commit messages: `feat:`, `exp:`, `docs:`, `data:`, `fix:`

_Last updated: 2025-08-26 05:58:11_

# KryptosCipher — K4 research workspace

**2026-10-07 update:** [Opus's independent review](docs/OPUS_K4_REVIEW.md) and a
[bounded keyword-progressive experiment](docs/KEYWORD_PROGRESSIVE_REPORT.md) are
now included. The new experiment tests 617,732 keyword alphabets and every cycle
drift at periods 1–24. Periods 1–23 have no compatible fit; period 24 has six weak,
incomplete fits, compared with a mean of 18 in shuffled controls. No additional
confirmed plaintext or solution was recovered.

**2026-10-07 Astra audit:** K4 remains unsolved in this repository. The period-27
scaffold below is a historical hypothesis, not an established cipher structure:
its 24 known letters constrain 24 different residues and perform zero independent
repeat checks. Phase changes do not constitute transposition experiments.

Read [the evidence report](docs/ASTRA_K4_REPORT_2026-10-07.md) for corrected findings,
bounded new experiments, exact scopes, and remaining uncertainties. Reproduce the
original Astra work using standard-library Python:

```bash
python3 -m unittest discover -s tests -p 'test_astra_research.py' -v
python3 -m research.run_astra
```

Opus and keyword-progressive code require NumPy. Their dictionary experiments also
require the registered `/usr/share/dict/web2` bytes; the progressive CLI accepts
`--dictionary PATH` and checks its hash. With those inputs available:

```bash
python3 -m unittest discover -s tests -v
python3 -m research.keyword_progressive --outdir out/progressive_reproduction
```

The [next research steps](docs/NEXT_STEPS.md) explain what the archive sale changes,
why the old period-27 track should be deprioritized, and which new hypotheses can
be tested without fitting a desired plaintext.

The older exports and notes below are retained for provenance. Their claims are
superseded where the audit identifies unsupported conclusions.

## Historical period-27 baseline

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
- Ordinary ABC Vigenere periods 1–26 and 30–52 conflict with the public cribs.
- Period-27 completion and phase sweeps lack independent supporting checks.
- Broader exclusions require the exact alphabet and key-family scopes in the reports.
- Earlier claimed grid, lamp-count and tableau eliminations lack executable evidence
  in this repository and are not treated as established exclusions.

## Contributing
- Prefer small JSON/CSV exports over large dumps.
- When an approach is ruled out, add a line to `DEAD_ENDS.md` and update `docs/analysis.md`.
- Use clear commit messages: `feat:`, `exp:`, `docs:`, `data:`, `fix:`

_Last updated: 2025-08-26 05:58:11_

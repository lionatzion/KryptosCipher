
# Kryptos K4 — Period‑27 Keystream + Minimal Route Transposition

A reproducible research repo aimed at cracking **Kryptos K4** under a **two‑layer cipher** hypothesis:

1. A minimal **route transposition** on a 7×14 grid (98 cells with one null), guided by the designer’s directional tips **“EAST”** then **“NORTHEAST”** and the left‑panel superscript **“YAR”**.
2. A **repeating Vigenère‑style keystream with period 27** that fits all four confirmed plaintext islands and Sanborn’s meta‑tells.

This repository includes scripts, notebooks, and data exports that let you sweep the remaining degrees of freedom, reproduce top candidates, and evaluate micro‑transposition variants under strict acceptance criteria.

---

## Executive Summary

The working model treats K4 as a final Vigenère‑style layer of **period 27** applied after a small, reversible transposition. The following **plaintext islands** are enforced:

- `EAST` at positions 22–25
- `NORTHEAST` at positions 26–34
- `BERLIN` at positions 64–69
- `CLOCK` at positions 70–74

In addition, **zero‑shift (“A”)** is enforced at cipher positions **33** and **74**. These anchors determine **24 of the 27** keystream letters; only residues **r7, r8, r20** remain unknown. Exhaustively filling those three residues (26³) and ranking by an English fitness yields top candidates that naturally bridge the islands, e.g. `... EAST NORTHEAST OF ... BERLIN CLOCK ...`.

A lightweight, optional **micro‑transposition phase** (keystream phase rotation as a proxy for tiny reversible path shifts) is provided. Variants are accepted **only** if they improve local function‑word density around the islands according to a strict filter.

---

## Repository Layout

- `scripts/`
  - `kryptos_k4_p27_sweep.py`  Period‑27 constraint‑driven keystream sweep and scoring
  - `k4_p27_sweep_phased_min.py`  Minimal phased sweep for micro‑transposition style tests
  - `route_transposition.py`  7×14 grid helpers; E→NE placeholder route (reversible)
  - `scoring.py`  English fitness (letter chi‑square + bigrams + function words)
- `notebooks/`
  - `candidate_exploration.ipynb`  Inspect and filter candidates
  - `lm_scoring_analysis.ipynb`  Score distribution and function‑word analysis
  - `transposition_visualization.ipynb`  Grid route exploration
- `data/`
  - `K4_ciphertext.txt`  Standard 97‑character K4 ciphertext
  - `out/`  Fresh results from your last runs, including `phase_min_*` variants
  - Historical exports such as `k4_top10_summary.json`, `k4_top100_candidates_light.csv`
- `docs/`
  - `hypothesis.md`  Full two‑layer model rationale
  - `analysis.md`  Eliminated methods and what to pursue next
- Top level
  - `main.py`  Orchestrates the P=27 sweep and prepares outputs
  - `phase_summary.json`  Results of the stricter acceptance filter across phase variants
  - `manifest.csv`  File inventory with sizes and hashes
  - `requirements.txt`  Minimal Python dependencies

---

## Installation

```bash
# Optional: create and activate a virtual environment
# python -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt
```

The code requires only standard Python 3 and `numpy`, `pandas`. Jupyter users can open the notebooks directly.

---

## Quick Start

Run the baseline period‑27 sweep and write outputs to `data/out`:

```bash
python main.py --outdir data/out --topn 100
```

Run the sweep script directly with more control:

```bash
python scripts/kryptos_k4_p27_sweep.py --outdir data/out --topn 100 --period 27
```

Review top results:

- `data/out/k4_top100_candidates_light.csv`
- `data/out/k4_top10_summary.json`

Open the exploration notebook:

```text
notebooks/candidate_exploration.ipynb
```

---

## Hypothesis Details

Ciphertext length is 97 characters. We model a **7×14** grid (98 cells) with one null and follow a path that begins **EAST** and then turns **NORTHEAST**. After transposition, a **repeating keystream of length 27** decrypts the text. The islands fix 24 residues of the cycle; only **r7, r8, r20** are unknown.

Scoring emphasizes **English function words** to reward plausible connective tissue between islands. We enforce that the known islands must appear exactly at the specified indices and that positions **33** and **74** are zero‑shift (**‘A’**).

Why 27:
- Periods 2–26 cannot satisfy all island constraints simultaneously.
- 27 aligns with the sculpture’s tableau anomaly, hinting at a 27‑tick cycle.
- 28/29 are kept only for a one‑time completeness check; they underperform and introduce conflicts.

---

## Micro‑Transposition Variants

We provide a minimal **phase‑rotation** proxy for tiny reversible route adjustments. For phase values in `{0, +1, −1, +14}`, the phased sweep:
1. Applies the same constraints with a keystream **phase offset**.
2. Decrypts and re‑scores the plaintext.
3. Writes results to `data/out/phase_min_{phase}/`.

### Stricter Acceptance Filter

We accept a variant over baseline **only if** function‑word hits increase within a **±8‑character window** around each island. The filter considers `THE`, `OF`, `IN`, `ON`. It writes a summary to:

```text
phase_summary.json
```

Fields include:
- Baseline metrics
- Each variant’s top candidate, keystream, score, and local function‑word hits
- Winner under the acceptance rule

You can tune the window or word list in `phase_summary.json` logic if you extend the scripts.

---

## Reproducing the Latest Results

1. Baseline sweep:
   ```bash
   python scripts/kryptos_k4_p27_sweep.py --outdir data/out --topn 100 --period 27
   ```
2. Micro‑phase variants:
   ```bash
   python scripts/k4_p27_sweep_phased_min.py --outdir data/out/phase_min_00 --topn 100 --period 27 --phase 0
   python scripts/k4_p27_sweep_phased_min.py --outdir data/out/phase_min_01 --topn 100 --period 27 --phase 1
   python scripts/k4_p27_sweep_phased_min.py --outdir data/out/phase_min_26 --topn 100 --period 27 --phase 26
   python scripts/k4_p27_sweep_phased_min.py --outdir data/out/phase_min_14 --topn 100 --period 27 --phase 14
   ```
3. Inspect `phase_summary.json` for the acceptance decision.

---

## What’s Eliminated

1. **Raw Berlin‑Clock lamp‑count → shift mappings** fail against the 24 fixed keystream constraints and score poorly.
2. **Naïve tableau pointer walks** do not reproduce the observed 27‑cycle or the island placement.
3. **Periods 2–26** incompatible with constraints.
4. **Periods 28/29** remain for a one‑time completeness pass only; they have lower scores and introduce conflicts.

---

## Roadmap

1. Finish the period‑27 cycle deterministically and freeze the winning keystream.
2. Probe minimal reversible route adjustments only if they improve local function words without harming islands.
3. Run a single completeness sweep for periods 28 and 29 and archive results.
4. Publish a concise “recipe” documenting ciphertext → (optional) route → P=27 keystream → plaintext, with top‑N and verification steps.

---

## Data and Reproducibility

- Key exports live under `data/` and `data/out/`.
- `manifest.csv` lists all files with SHA‑256 hashes.
- Notebooks are provided for transparent, interactive review of candidates and scoring.

---

## Contributing

Please open a discussion or pull request for:
- Alternative but reversible route definitions that retain island indices.
- Improved language models or scoring functions.
- Additional acceptance metrics focused on function‑word bridges around islands.

---

## Credits

Thanks to the Kryptos community and prior publications. This repo packages a constraint‑driven, clue‑consistent approach and makes it easily reproducible for external review.

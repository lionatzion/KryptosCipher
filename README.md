# KryptosCipher

A reproducible Python workbench for investigating Kryptos K4, the final
97-character passage on Jim Sanborn's sculpture.

**Project status: November 23, 2026. No verified K4 solution or additional
confirmed plaintext has been recovered by this project.**

The verified workbench and review corrections were merged in
[PR #1](https://github.com/lionatzion/KryptosCipher/pull/1). The project now has
working K1–K3 baselines, explicit K4 constraints, reproducible bounded experiments,
and a record of which conclusions the evidence supports. The next stage is to
test the remaining specified hypotheses with registered inputs and controls.

## Where the project stands

| Area | Current status |
|---|---|
| K1–K3 | Expected plaintexts and exact ciphertext round trips pass, including both carved and corrected K2 |
| K4 plaintext | 24 public anchor letters; the remaining 73 positions are unconfirmed |
| Implementation | Anchor constraints, both substitution/transposition orders, explicit key completion budgets, diagnostics and separate scoring windows |
| Validation | 56 tests passed locally; Python 3.11 and 3.13 checks passed for the merged review commit |
| Language scoring | Scorer and matched controls implemented; production English calibration still requires an external quadgram count table |
| Next research | Three bounded experiments specified in the active roadmap; those campaigns have not been executed |

The four confirmed anchors are fixed at these **one-based positions**. Code uses
zero-based indices.

| Plaintext | Positions | Ciphertext |
|---|---|---|
| EAST | 22–25 | FLRV |
| NORTHEAST | 26–34 | QQPRNGKSS |
| BERLIN | 64–69 | NYPVTT |
| CLOCK | 70–74 | MZFPK |

The [research dossier](docs/RESEARCH_DOSSIER.md) separates creator statements and
archive history from locally tested models. It records the Alexanderplatz World
Clock identification. That referent does not establish a 24-step key generator.
YAR, the extra L and sculpture geometry remain physical research leads requiring
an explicit, testable interpretation.

## Verified results and their limits

| Finding | What the result actually covers |
|---|---|
| Direct periods 1–26 conflict with the anchors | Original alignment, STD/STD or KRYPTOS/KRYPTOS alphabets, Vigenere, Beaufort and variant Beaufort; no added masking or transposition |
| A constant gap between intact crib blocks does not rescue periods 1–23 | Every relative phase in those six fixed tableau conventions |
| The tested numeric World Clock catalog has no exact anchor match | 243,648 schedule/route configurations; other clock constructions remain open |
| The tested base-12 recurrence has no exact fit | 1,492,992 model/primer checks across six defined models, five-digit primers and fixed taps (5,4) |
| Period 27 is compatible but not established | The 24 anchors occupy distinct residues, giving zero independent repeat checks and leaving three free key values |
| Crib parity is an observed relation | It does not prove that the whole key alternates parity or identify the order of cipher layers |

The [hypothesis ledger](docs/HYPOTHESIS_LEDGER.json) gives assumptions and evidence
for each exclusion. The [executed November evidence](out/november_20261123/README.md)
contains commands, outputs, controls and hashes. These are bounded conclusions,
not an elimination of all classical or multilayer ciphers.

The earlier preferred period 27 model, function-word acceptance rules and lamp
clock interpretation are no longer active guidance. The claimed Gemini campaign
of 61.8 million configurations has not been reproduced here and is not counted as
local evidence. Historical candidate scores are not validated English rankings.
See the [retired claims](docs/RETIRED_CLAIMS.md) for the corrections.

## Run the workbench

Use Python 3.11 or newer. Run these commands from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
python -m kryptos verify
python -m kryptos diagnostics --output out/local/diagnostics.json
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead. The
`kryptos` package uses the standard library; the full tests and research audits
also use NumPy and JSON Schema validation, installed by the `test` extra.

`verify` checks K1, carved K2, corrected K2 and K3. It does not verify a K4 answer.
The root `python kryptos_analysis.py verify` command provides the same interface
after installation.

Reproduce the recorded audits without overwriting the committed evidence:

```bash
python -m research.verify_report_claims --output out/local/independently_checked.json
python -m research.review_checks --output out/local/review_checks.json
python -m research.november_audit --output out/local/algebraic_audit.json
python -m kryptos clock --routes grids --output out/local/clock.json
```

For search options, run `python -m kryptos --help`. Scored searches require
`--quadgrams /path/to/english_quadgrams.txt`. No English corpus is bundled.
Without it, output is unscored enumeration order. Searches that reach a budget
report `complete: false`; they must not be reported as exhaustive exclusions.

## Next experiments

1. **Bounded base-10 keyword Gromark.** Register a wordlist and filter ciphertext
   alphabets, then test five-digit recurrence primers with an arbitrary injective
   plaintext alphabet. Separate overlap with the October experiments.
2. **Specified parity generators.** Test a small set of independently motivated
   key rules, with a comparison branch that does not assume alternating parity.
3. **Physical or positional masking.** Define reversible rules involving measured
   geometry, YAR, interrupted key advancement or rearrangement that cannot reduce
   to the already excluded constant phase shift between intact cribs.

These are proposals, not discoveries. The [active roadmap](docs/ACTIVE_ROADMAP.md)
sets equations, prerequisites, controls, limits and stopping rules. The first
action is to register the Gromark inputs and scope and pass planted recovery
controls before running its K4 search. Any language-based evaluation also needs
a documented corpus and calibration of the complete search procedure.

## Evidence required from a new experiment

- Freeze the model, input hashes, parameters, budget and seeds before inspecting
  K4 results. Demonstrate recovery on novel synthetic messages and keys.
- Enforce the known anchors and report free parameters. Collision counts describe
  evidence strength; they are not a hard rejection rule for a consistent model.
- Keep quadgram windows separate: 64 entirely unknown, 12 crossing an anchor
  boundary, 18 entirely within anchors, and 94 in the full text. Do not splice the
  73 unknown letters together to invent adjacencies.
- Compare the complete search with both histogram-preserving shuffles and uniform
  controls under the same budgets. Do not transfer an old score cutoff to a new
  corpus or scoring method.
- `--evaluation-holdout` withholds BERLINCLOCK from fitting, but both public cribs
  influenced the research. It is not an untouched blind test.
- Require ciphertext reconstruction and independently supported plaintext. A
  round trip or a fluent sentence produced by a flexible model is not a solution.

No command submits candidates to an external verifier or incurs verification fees.

## Project navigation

| Path | Purpose |
|---|---|
| [src/kryptos/](src/kryptos/) | Current primitives, constraints, scoring, diagnostics and command line interface |
| [tests/](tests/) | Known answers, synthetic recovery controls and research regressions |
| [docs/ACTIVE_ROADMAP.md](docs/ACTIVE_ROADMAP.md) | Current next experiments |
| [docs/RESEARCH_DOSSIER.md](docs/RESEARCH_DOSSIER.md) | Source references, interpretation and methodological limits |
| [docs/HYPOTHESIS_LEDGER.json](docs/HYPOTHESIS_LEDGER.json) | Scoped exclusions, open models and unverified reports |
| [out/november_20261123/](out/november_20261123/) | Recorded audit outputs and provenance manifest |
| [research/](research/) | Reproduction scripts and earlier experiment implementations |
| [docs/LEGACY_ARTIFACTS.md](docs/LEGACY_ARTIFACTS.md) | File-specific treatment of older scripts, notebooks and exports |

Older notes and results are retained for provenance, not as current instructions.
The export audit distinguishes 110 rows requiring phase 26, 155 reproducing at
phase 0, and two incomplete records. These are consistency findings, not candidate
solutions. Start new work from this README, the active roadmap and the ledger.

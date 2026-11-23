# Executed November evidence

Date: November 23, 2026. Python 3.12 in the local validation environment.
No K4 solution, English corpus calibration or paid verifier submission is claimed.

| Artifact | Executed result |
|---|---|
| `independently_checked.json` | First report audit: independent K1–K3 checks, 240 direct periodic cases, window partition and zero-collision counterexample |
| `review_checks.json` | Seven named repository exports: 110 phase-26 rows, 155 phase-0 rows, two incomplete records; five period-24 conflicts in each of six modes |
| `diagnostics.json` | Four baseline cases pass; 180 direct models across two alphabets, three modes and periods 1–30; only periods 27–29 compatible |
| `clock.json` | 846 route/alphabet/mode/order models times 288 distinct schedules = 243,648 configurations; zero exact matches |
| `algebraic_audit.json` | 2,106 relative-phase checks, 104 arbitrary-alphabet graph models, 961 binary recurrence/seed pairs, 1,492,992 base-12 model/primer checks; 36 synthetic controls pass |
| `tests.txt` | 56 tests pass, including source-specific export checks, independent audit cross-checks and earlier research regressions |
| `manifest.json` | Source/output hashes, Python/NumPy versions, seeds, exact commands and original-to-repository artifact mapping |

Reproduce from the repository root:

```bash
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
python -m research.verify_report_claims --output out/local/independently_checked.json
python -m research.review_checks --output out/local/review_checks.json
python -m kryptos diagnostics --output out/local/diagnostics.json
python -m kryptos clock --routes grids --output out/local/clock.json
python -m research.november_audit --output out/local/algebraic_audit.json
```

Output timestamps, requested destination and elapsed seconds can differ. The
mathematical results should agree. The first audit reproduces its saved JSON
exactly while its source and input hashes remain unchanged. CLI envelopes validate against
`docs/EXPERIMENT_SCHEMA.json`; the detailed algebraic audit has its own recorded
schema and script hash. Its 36 assertions include planted phase, alphabet and
recurrence checks. It does not claim to reproduce Gemini's entire search campaign.

The evidence-archive script `audit_parity_nulls.py` is already included as
`research/november_audit.py`, with `audit_results.json` recorded here as
`algebraic_audit.json`. The first suite is `research/verify_report_claims.py`;
only its default repository paths and output-directory creation were adapted.
The original legacy script is preserved byte for byte in `docs/archive/`.
These mappings avoid duplicate implementations and conflicting current outputs.

The review audit corrects a source-scope error in the November note: the earlier
seven-row position-21 mismatch concerned another uploaded JSON version, not the
root GitHub exports. It records exact filenames and input hashes, including the
five-row CSV's `Plaintext_highlighted` field. Earlier audit output is preserved;
the [historical inventory](../../docs/LEGACY_ARTIFACTS.md) explains the distinction.

The first full local test attempt exposed an old `/usr/share/dict/web2` dependency.
The algorithm tests now use deterministic synthetic keywords plus the original
context words; all four formerly dependent tests execute. The October dictionary
experiment, its registered hash and its saved results were not altered or rerun.

The matched-control pipeline is tested using a deliberately tiny synthetic score
table, not represented as an English research corpus. Real language calibration
requires an external count table and the exact same model catalog, key-completion
policy and search budget for observed and randomized ciphertexts. See README for
the complete pipeline command. No numerical English significance claim is made.

Original and current manifests from October remain intact. New output counts must
not be added to unverified external totals as independent evidence.

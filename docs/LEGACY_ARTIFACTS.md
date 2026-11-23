# Historical artifact inventory

These files are retained at their original paths to preserve older commands,
notebooks and hash manifests. Use the `src/kryptos/` package for current work.
Reproduce this inventory with:

```bash
python -m research.review_checks --output out/local/review_checks.json
```

The committed [output](../out/november_20261123/review_checks.json) records each
file's SHA-256 and each row's reproduction result. These are key/plaintext
consistency checks, not validated language scores or K4 solutions.

| Historical file | Rows | Interpretation |
|---|---:|---|
| `k4_top10_summary.json` | 10 | All require unrecorded phase 26 |
| `k4_top100_candidates_light.csv` | 100 | All require unrecorded phase 26 |
| `kryptos_k4_top50_period27.csv` | 50 | All reproduce at phase 0 |
| `kryptos_k4_top100_period27_quadgram_composite.csv` | 100 | All reproduce at phase 0 |
| `Top_5_K4_candidates_with_highlighted_phrases.csv` | 5 | `Plaintext_highlighted` is complete text; all reproduce at phase 0 |
| `data/exports/k4_top10_summary.json` | 1 | Incomplete `...` demonstration placeholder; never a plaintext candidate |
| `data/exports/k4_top100_candidates_light.csv` | 1 | Summary without plaintext; cannot validate a plaintext/key pair |

The phase convention is `P[i] = (C[i] - key[(i + phase) % 27]) mod 26` in standard
alphabet indices, with zero-based `i`. Keep historical file bytes unchanged;
consumers must supply phase 26 for the first two files. Do not confuse them with
similarly named project uploads. The October audit ignored the highlighted-text
field in the five-row CSV; this audit explicitly accepts that named field and
validates its complete length and characters.

`README_K4_exports.md` and `.txt`, the root period 27 scripts and the notebooks are
historical. Their older scores and proposed geometry are not current findings.
`route_transposition.py` contained an identity placeholder under an E-to-NE name.
Calling that unimplemented traversal now raises `NotImplementedError`; implemented
route choices live in `kryptos.primitives.route_catalog`.

`out/astra_20261007/feedback.json` and
`out/opus_review_20261007/reproduction/feedback.json` are byte-identical. Both are
retained as the original run and its recorded reproduction, with their existing
manifest paths intact. They must not be counted as extra independent search
coverage. Their common hash is checked in the review audit.

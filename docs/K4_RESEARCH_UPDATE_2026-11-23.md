# Kryptos K4: research update

**November 23, 2026 · Ryan Scarborough · Status: no verified decryption**

This project asks which candidate mechanisms can explain Kryptos K4's 97-letter ciphertext, not which guessed sentence sounds most plausible. The public repository's period-27 sweep is a baseline, not a solution. The [October research PR](https://github.com/lionatzion/KryptosCipher/pull/1) records earlier work, including why period 27 is underconstrained and why the World Clock is the stronger referent. This note separates checks that can be independently reproduced from results reported in the newer working audit.

## What is fixed

The canonical K4 transcription starts at `OBKR` and ends at `KCAR`; the physical question mark before it is not part of K4. All positions below are **one-based within K4**. Two known plaintext blocks fix 24 letters: `EASTNORTHEAST` at **22–34** and `BERLINCLOCK` at **64–74**. The remaining 73 letters are not public ground truth. See the [CIA sculpture reference](https://www.cia.gov/legacy/headquarters/kryptos-sculpture/), [Paradigm's indexed K4](https://www.paradigm.xyz/kryptos/) and [the research dossier's crib provenance](https://github.com/rayborg/kryptos-k4-dashboard/blob/main/docs/RESEARCH.md#k4-public-plaintext).

The archival recovery and the cryptanalysis are separate. Jarett Kobek and Richard Byrne recovered the plaintext from Sanborn's papers, and Sanborn confirmed it; that does not give us a publicly reproducible method from the sculpture. [Archival discovery account](https://www.scientificamerican.com/article/a-solution-to-the-cias-kryptos-code-is-found-after-35-years/) · [Paradigm's stewardship and verification statement](https://www.paradigm.xyz/writing/kryptos)

## A check you can reproduce

For a direct additive cipher using one fixed alphabet, the shift at position `i` is `(index(ciphertext[i]) - index(plaintext[i])) mod 26`. A period-24 key must use the same shift at positions 48 letters apart. All five pairs below require different shifts. Within each cell, the first and second values correspond to the first and second positions:

| One-based positions | Ciphertext | Known plaintext | A–Z shifts | KRYPTOS-alphabet shifts |
|---|---|---|---:|---:|
| 22 / 70 | F / M | E / C | 1 / 10 | 1 / 9 |
| 23 / 71 | L / Z | A / L | 11 / 14 | 10 / 8 |
| 24 / 72 | R / F | S / O | 25 / 17 | 21 / 7 |
| 25 / 73 | V / P | T / C | 2 / 13 | 18 / 20 |
| 26 / 74 | Q / K | N / K | 3 / 0 | 1 / 0 |

The second alphabet is `KRYPTOSABCDEFGHIJLMNQUVWXZ`. All five conflicts also hold under Beaufort and variant Beaufort, using their own shift equations. The [reproducible review audit](../out/november_20261123/review_checks.json) lists all 30 witnesses; the [direct diagnostics](../out/november_20261123/diagnostics.json) cover periods 1–30. Every period 1–26 fails under these six fixed-alphabet models. These results do not rule out irregular clock schedules, clock-driven permutations or layered constructions. Sanborn's clock identification is evidence about the referent, not proof of a 24-step key. [Dossier's source links](RESEARCH_DOSSIER.md#sources-and-engineering-references)

Period 27 has a different problem: the 24 known letters occupy 24 **distinct** residues. Fitting all 24 therefore checks no repeated shift among them and leaves three free residues. The fit does not validate the period. Positions 21 and 75 both have ciphertext `W` and share a period-27 residue, so those two positions must decrypt alike in that model.

The repository's root `k4_top10_summary.json` and `k4_top100_candidates_light.csv` contain 110 rows whose stored plaintexts require phase **26**, using `key[(i + 26) % 27]` with zero-based `i`. Neither file records that phase; at phase 0 none reproduces its stored plaintext. With phase 26 all 110 match. The other three complete root CSVs contain 155 rows consistent at phase 0. An earlier seven-row mismatch statement referred to a different uploaded version and did not describe these repository files. The [export inventory](LEGACY_ARTIFACTS.md) and hashed [audit output](../out/november_20261123/review_checks.json) now identify the exact files tested.

## What the newer work adds

- **Historical controls.** The included workbench verifies K1, carved K2, corrected K2 and K3 against expected plaintexts and exact round trips. [K2 correction record](https://www.elonka.com/kryptos/CorrectedK2Announcement.html) · [Executed evidence](../out/november_20261123/README.md)
- **Synthetic controls.** The included tests recover planted cases in both substitution/transposition orders, selected fixed clock schedules, and a zero-collision construction. These show recovery within the modeled families; they do not establish K4's method.
- **Real K4.** Both independent audit suites now ship as `research/verify_report_claims.py` and `research/november_audit.py`, with outputs and commands under [November evidence](../out/november_20261123/README.md). The included numeric clock/route subset tests 243,648 configurations with zero exact anchor matches. The larger **61.8 million** Gemini campaign is still a separate, unprovided runner and remains reported rather than locally reproduced. No verified K4 plaintext or method resulted from the included bounded checks.

## What I would test next

The [active roadmap](ACTIVE_ROADMAP.md) gives the current experiment scopes. Bean's 39-primer baseline below is already a passing regression in `tests/test_opus_review.py`; it is a prerequisite to preserve, not an unperformed task.

1. **Keep Bean's Gromark baseline as a regression.** The current test reproduces the published five-digit, base-10 diagnostic's 39 compatible primers under its flexible alphabet constraints. These are not 39 plaintext solutions. Record the exact alphabet, offset, and search bounds when comparing a new experiment with this baseline. [Bean's HistoCrypt paper](https://doi.org/10.3384/ecp183153) · [Reference code](https://github.com/RichardBean/k4testing)
2. **Test whether a narrower rule predicts an unfitted block.** Freeze the key family, alphabet, route set, and ranking rule; choose parameters with only one crib block, then test exact recovery of the other without retuning. Because both blocks are already public, this is an evaluation holdout, not independent confirmation. Report the number of tested recipes and surviving keys, and compare the entire search on matched random controls. Use language scores as diagnostics, not proof; an English-only score can miss names or non-English fragments.
3. **Require a complete explanation.** A strong candidate gives all 97 letters, a fully specified reversible recipe, exact re-encryption to the canonical ciphertext, and evidence that the recipe was not merely built to force the answer. Paradigm's verifier can confirm a final plaintext submission, not the proposed historical method.

The [Rayborg research dossier](https://github.com/rayborg/kryptos-k4-dashboard/blob/main/docs/RESEARCH.md) is an external reference, not an output of this project.

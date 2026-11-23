# Kryptos K4: research update

**November 23, 2026 · Ryan Scarborough · Status: no verified decryption**

This project asks which candidate mechanisms can explain Kryptos K4's 97-letter ciphertext, not which guessed sentence sounds most plausible. The public repository's period-27 sweep is a baseline, not a solution. The [October research PR](https://github.com/lionatzion/KryptosCipher/pull/1) records earlier work, including why period 27 is underconstrained and why the World Clock is the stronger referent. This note separates checks that can be independently reproduced from results reported in the newer working audit.

## What is fixed

The canonical K4 transcription starts at `OBKR` and ends at `KCAR`; the physical question mark before it is not part of K4. All positions below are **one-based within K4**. Two known plaintext blocks fix 24 letters: `EASTNORTHEAST` at **22–34** and `BERLINCLOCK` at **64–74**. The remaining 73 letters are not public ground truth. See the [CIA sculpture reference](https://www.cia.gov/legacy/headquarters/kryptos-sculpture/), [Paradigm's indexed K4](https://paradigm.xyz/kryptos/) and [the research dossier's crib provenance](https://github.com/rayborg/kryptos-k4-dashboard/blob/main/docs/RESEARCH.md#k4-public-plaintext).

The archival recovery and the cryptanalysis are separate. Jarett Kobek and Richard Byrne recovered the plaintext from Sanborn's papers, and Sanborn confirmed it; that does not give us a publicly reproducible method from the sculpture. [Archival discovery account](https://www.scientificamerican.com/article/a-solution-to-the-cias-kryptos-code-is-found-after-35-years/) · [Paradigm's stewardship and verification statement](https://www.paradigm.xyz/writing/kryptos)

## A check you can reproduce

For a direct additive cipher using one fixed alphabet, the shift at position `i` is `(index(ciphertext[i]) - index(plaintext[i])) mod 26`. A period-24 key must use the same shift at positions 22 and 70, which are 48 letters apart. The confirmed pairs require different shifts:

| One-based position | Ciphertext | Known plaintext | A–Z shift | KRYPTOS-alphabet shift |
|---|---|---|---:|---:|
| 22 | F | E | 1 | 1 |
| 70 | M | C | 10 | 9 |

The second alphabet is `KRYPTOSABCDEFGHIJLMNQUVWXZ`. This rules out **direct, repeating period-24 addition with either of these fixed alphabets**. It does not rule out an irregular clock schedule, a clock-driven permutation, or a layered construction. Sanborn's identification of the Alexanderplatz World Clock is evidence about the referent, not proof that the cipher uses a 24-step key. [Dossier's summary and source links](https://github.com/rayborg/kryptos-k4-dashboard/blob/main/docs/RESEARCH.md#final-2025-clues)

Period 27 has a different problem: the 24 known letters occupy 24 **distinct** residues. Fitting all 24 therefore checks no repeated shift among them and leaves three free residues. The fit does not validate the period. In a separate audit of saved candidates, seven entries disagreed with their own recorded keys at position 21. Positions 21 and 75 both have ciphertext `W` and share a period-27 residue, so those two positions must decrypt alike in that model. Treat the disagreement as an export inconsistency, not a clue about the missing letter.

## What the newer work adds

- **Historical controls.** The working audit reports restoring exact K1–K3 checks, treating the carved K2 and its documented missing-`S` correction as separate cases, and reproducing K3 with a two-stage rotation. [K2 correction record](https://www.elonka.com/kryptos/CorrectedK2Announcement.html) · [K3 reference route](https://github.com/rayborg/kryptos-k4-dashboard/blob/main/docs/RESEARCH.md#exact-reproducible-route)
- **Synthetic controls.** The working solver report describes recovery on synthetic cases for both substitution/transposition orders and selected clock-based constructions. Those tests show that the checks can recover examples built within the modeled families; they are not evidence that K4 uses one of those mechanisms.
- **Real K4.** The working report describes bounded sweeps over keyed substitutions, both composition orders, and selected World Clock mappings and grid routes. No verified K4 plaintext or method resulted. That is a result about the searched configurations, not an exclusion of all clock or transposition ciphers. The newer runner and sweep logs are not included in this update, so those larger runs remain reported rather than independently reproduced here.

## What I would test next

1. **Reproduce Bean's Gromark baseline separately.** Start with the published five-digit, base-10 diagnostic and its stated alphabet assumptions. The companion code reports 39 compatible primers under flexible alphabet choices; these are not 39 plaintext solutions. Record the exact alphabet, offset, and search bounds before comparing results. [Bean's HistoCrypt paper](https://doi.org/10.3384/ecp183153) · [Reference code](https://github.com/RichardBean/k4testing)
2. **Test whether a narrower rule predicts an unfitted block.** Freeze the key family, alphabet, route set, and ranking rule; choose parameters with only one crib block, then test exact recovery of the other without retuning. Because both blocks are already public, this is an evaluation holdout, not independent confirmation. Report the number of tested recipes and surviving keys, and compare the entire search on matched random controls. Use language scores as diagnostics, not proof; an English-only score can miss names or non-English fragments.
3. **Require a complete explanation.** A strong candidate gives all 97 letters, a fully specified reversible recipe, exact re-encryption to the canonical ciphertext, and evidence that the recipe was not merely built to force the answer. Paradigm's verifier can confirm a final plaintext submission, not the proposed historical method.

The [Rayborg research dossier](https://github.com/rayborg/kryptos-k4-dashboard/blob/main/docs/RESEARCH.md) is an external reference, not an output of this project.

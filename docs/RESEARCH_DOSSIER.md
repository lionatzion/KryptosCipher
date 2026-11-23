# Kryptos research dossier

Version 2026-11-23. This consolidates `Kryptos notes.txt`, `Kryptos expandes.txt`
and `Kryptos theories.txt`, preserving their original bytes under
[archive](archive/README.md). It supersedes their confidence claims, not the
historical record. No K4 solution is asserted.

## Evidence levels

1. **Primary source:** creator statement, official steward statement or published
   research with its own methods. A statement about intent is not an algorithm.
2. **Locally executed:** exact inputs, code and output included with positive
   controls. An elimination applies only to its stated equations and bounds.
3. **External research:** credited community results not necessarily rerun here.
4. **Reported or speculative:** unsupported sweep counts, guessed text,
   historical city reconstructions and proposed physical interpretations.

The hypothesis ledger separates `eliminated`, `statistical`, `sampled_null`,
`open`, `unverified` and `retired`. Exhausting a finite catalog does not exhaust a
general cipher family. Raw counts across equivalent models are not independent
evidence. Vigenere and variant Beaufort with unrestricted keys are equivalent
under key negation.

## Status and chronology

| Date | Evidence and implication | Source |
|---|---|---|
| April 2006 | K2's intended ending is XLAYERTWO. Keep the carved IDBYROWS result separately. | S1, primary correction account |
| September 2025 | Kobek and Byrne recovered K4 plaintext from archival material; Sanborn confirmed the recovery. This did not publicly supply a cryptanalytic derivation. | S2, steward account; November note links discovery reporting |
| November 2025 | The clock referent was clarified as the World Clock at Alexanderplatz. The Mengenlehreuhr lamp interpretation is retired. | S3, creator letter |
| November 20, 2025 | Sanborn's archive sold for $962,500. | S4, auctioneer |
| June 12, 2026 | Paradigm announced stewardship and a paid plaintext verifier, describing an answer-blind SHA-256/HMAC procedure and $1 submission charge. | S2, steward |
| November 23, 2026 | This repository has no verified new K4 plaintext. November outputs reproduce only the stated bounded checks. | Included code and logs |

S2 also discusses a separate K5. Its existence and Paradigm's practice challenges
do not establish a particular K4 model. We do not infer K4's method from the CTF
or claim an independently verified CTF completion timeline. Service availability
and prices can change. This workbench made no paid submissions.

## Canonical data and baselines

Code uses zero-based indices; source discussions often use one-based positions.
K4 is exactly 97 letters and excludes the preceding physical question mark.

| Plaintext | One-based positions | Ciphertext |
|---|---|---|
| EAST | 22–25 | FLRV |
| NORTHEAST | 26–34 | QQPRNGKSS |
| BERLIN | 64–69 | NYPVTT |
| CLOCK | 70–74 | MZFPK |

K1 uses PALIMPSEST over `KRYPTOSABCDEFGHIJLMNQUVWXZ`. K2 uses ABSCISSA over that
alphabet and preserves three question marks without advancing the key. The
corrected input inserts S at raw index 364 after NUPLGE. Original and corrected
inputs independently round trip. K3 decrypts 336 letters with counterclockwise
rotations at 24 columns and then 8 columns; carry its final question mark
separately. Inverse rotations use 42 and then 14 columns.

Expected plaintext fixtures are independent of the decoder output. IQLUSION,
UNDERGRUUND and DESPARATLY remain unchanged; the fixture does not assert that
every spelling difference was intentional. The uploaded legacy optimizer was a
monoalphabetic teaching example, not a viable K4 solver: the same cipher S must
produce plaintext S and T at positions 33 and 34. The new package imports none of
that optimizer or its bigram scoring. That uploaded file was not previously part
of the public repository; the new root file is a compatibility entry point.

## Consolidated hypothesis review

| Original approach | Current treatment |
|---|---|
| 1, 2, 5, 7: lamp rows, quarters, base-5 timestamps | Retire the claimed clock identification. Generic mathematical constructions need their own rationale and tests. |
| 3, 8: YAR reading instruction or tableau origin | Retain as open physical clues. Register coordinates, direction, mirroring and wrapping before testing. YAR does not prove a particular mnemonic. |
| 4: fractionation or extra L as a rotor | Open at the broad family level. Unpublished Playfair/Bifid/Trifid counts are not imported as eliminations. |
| 6: bearing and sculpture overlay | Open with measured geometry. Approximately 44 degrees is northeast; east-northeast is 67.5 degrees. State coordinates and rounding. |
| 9: anchor constrained reconstruction | Implemented for named finite periodic and route models. Fitted text is not newly discovered plaintext. |
| Hill matrices and surface regression | Extra L alone supplies no matrix dimension or invertibility evidence. No blanket exclusion of all Hill models or proof of an overlay is claimed. |

The Weltzeituhr's 24 facets motivate possible schedules, not a mandatory period.
The engine tests numeric sequences 0..23, 1..24 and -11..12 modulo 26, all phases,
directions and signs, deduplicating identical sequences. Routes skip trailing
unfilled grid cells; those cells are not plaintext nulls. Historical city lists,
modern engravings and compass rounding rules are not interchanged. No official
1989 24-city list is supplied by this project.

## Reproduced November results and boundaries

- Direct STD and KRYPTOS periodic Vigenere/Beaufort/variant Beaufort models fail
  periods 1–26. Among 1–30, 27–29 fit because all 24 anchors have distinct residues.
  Period 27 has 17,576 completions and no independent repeat check.
- All relative phases through period 26 require 2,106 checks. Every phase fails
  at periods 1–23 if both crib blocks stay intact. One to four nulls only between
  the blocks cannot rescue periods 1–16. Nulls inside a crib, other alphabets,
  transpositions and irregular key advances lie outside that result.
- Four one-arbitrary-alphabet graph models exclude common periods 1–12, 14, 15,
  17, 18, 21, 22 and 25. Model-specific survivors and injective alphabet witnesses
  are saved. Graph reasoning covers arbitrary permutation alphabets without
  literally iterating 26! arrangements.
- All 248,832 base-12 five-digit primers fail in six stated alphabet/sign models
  at taps (5,4), totaling 1,492,992 model/primer checks. This does not cover every
  Gromark alphabet, recurrence, modulus, primer length or transposition.
- Crib parity has 13 pair matches and 11 independent equalities. It does not force
  the direct key to alternate globally. The 961 tested nonzero binary recurrence
  and seed pairs admit no genuine period-21 survivor under those constraints.
  Width-21 repeated bigrams are not thereby proved to arise from that recurrence.
- `DIAWINFBN` is at zero-based 55–63. Its final N encrypts the B of BERLIN. Its
  five lag-4 differences are +5 modulo 26.

These are locally executed checks. Gemini's claimed 61.8 million configurations
and the community's much larger archive totals have not been reproduced here.
Neither substitutes for a scoped exclusion record. Lean source availability is
not a claim that this repository ran the Lean toolchain.

## Scoring and falsification

The 94 contiguous quadgrams partition into 64 unknown-only, 12 boundary and 18
anchor-internal windows. Never join unknown runs into new adjacencies. Primary
ranking uses the unknown-only mean; boundary and full scores appear separately.
English scoring can penalize names, foreign words and abbreviated instructions,
so low scores never alone establish impossibility.

Corpus bytes, count convention and SHA-256 identify a scoring scale. No -5.20
gate, purported 9.41-sigma significance, or synthetic backoff calibration is
inherited from the unprovided Gemini solver. The pipeline repeats fitting,
completion limits and selection on uniform and histogram controls. It compares
best search results, not a selected maximum to an unsearched random sentence.
Its empirical ranks are conditional diagnostics; earlier hypothesis selection
and multiple experiments still matter. No production English score calibration
has been published with this update because no external corpus was supplied.

At period p, u observed key residues imply `24-u` consistency comparisons and
`p-u` free values when all anchors are used. Low comparison counts weaken evidence
but do not make a true construction impossible. Tests include a correct
zero-collision 24-period transposition-then-substitution example.

Evaluation holdout mode never fits BERLINCLOCK, but that public block influenced
the hypotheses. Novel seeded messages and keys supply separate recovery controls.
A round trip plus fluent text remains insufficient if a flexible recipe was built
to force that text.

## Next work

1. Reconcile a dictionary Gromark campaign with October experiment scopes. Freeze
   the exact alphabet rule and dictionary hash; deduplicate alphabets, preserve
   survivors and demonstrate planted recoveries.
2. Explore physical masking with a reversible, measured coordinate rule. Preserve
   YAR and extra L as clues without promoting an arbitrary overlay into a proven
   mechanism. Do not repeat excluded simple gap-phase cases under new names.
3. Study bounded nonperiodic shifts with parity as a conditional branch. Keep
   another branch that does not assume the pattern reflects the cipher.
4. Require a complete reproducible recipe and search-aware language evidence
   before considering a separately authorized official verifier submission.

## Sources and engineering references

- **S1:** [Kryptos Group / Elonka Dunin, K2 correction](https://www.elonka.com/kryptos/CorrectedK2Announcement.html).
- **S2:** [Paradigm, Project Kryptos](https://www.paradigm.xyz/writing/kryptos), June 12, 2026.
- **S3:** [Sanborn letter, November 12, 2025](https://www.documentcloud.org/documents/26229389-adobe-scan-nov-12-2025/), also indexed in the [Rayborg dossier](https://github.com/rayborg/kryptos-k4-dashboard/blob/main/docs/RESEARCH.md).
- **S4:** [RR Auction archive sale announcement](https://content.rrauction.com/jim-sanborns-complete-kryptos-archive-sells-for-962500-at-auction/).
- **S5:** [Richard Bean, HistoCrypt 2021 paper](https://richardbean.id.au/papers/03_Bean_HistoCrypt2021.pdf) and [companion code](https://github.com/RichardBean/k4testing).
- **S6:** [Colin Patrick / KryptosBot, crib parity](https://www.kryptosbot.com/crib-parity/) and [research archive](https://github.com/jcolinpatrick/kryptos).
- **Engineering references:** [nitsuah/kryptos](https://github.com/nitsuah/kryptos) for scoped ledger/positive controls; [rayborg/kryptos-k4-dashboard](https://github.com/rayborg/kryptos-k4-dashboard) for source organization; [SartajBhuvaji/kryptos-benchmark](https://github.com/SartajBhuvaji/kryptos-benchmark) for novel synthetic cases.

External projects are credited as ideas and sources, not imported as proof. No
third-party implementation was copied into this update. Preserve licenses and
attribution if importing their code or data later.

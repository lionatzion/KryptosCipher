# Bounded keyword-tableau progressive-key experiment

Recorded 2026-10-07, before the first K4 run of this new family. This document's
SHA-256 is saved before execution and embedded in the result. Its design is fixed;
implementation corrections must be logged separately.

## Question and motivation

Does a dictionary-generated substitution tableau fit K4 when the repeating key
increments by a constant once per cycle? K1/K2 motivate keyword alphabets. Astra
tested this progressive equation only with ABC/KRYPTOS alphabets; Opus tested a
large keyword-alphabet set with periodic and Gromark schedules. This experiment
combines the already documented alphabet set with the untested progressive schedule.
It does not assert that K4 actually uses any of these mechanisms.

## Fixed scope

- The 97-letter canonical K4 ciphertext and the 24 public crib letters in the
  existing core module. Positions are zero-based in arithmetic.
- Alphabet family: `/usr/share/dict/web2` plus Opus's 74 fixed context words, with
  the same `kryptos`, `continue`, and `columnar` constructions and deduplication.
  Expected dictionary SHA-256:
  `be41ad97963bf8dabedd5871d5d691596175269d540956b0f9965a885c2bbab9`.
  Expected unique alphabets: 617,732. Record actual dictionary and ordered-alphabet
  hashes. Stop if the registered input does not match.
- Plain/cipher configurations: W/W, W/ABC, ABC/W, W/KA, KA/W, plus ordered pairs
  of different context-word alphabets. W/W uses the same alphabet on both sides;
  it does not enumerate all pairs of unrelated dictionary words.
- Sign conventions: Vigenere `c=p+k`, Beaufort `c=k-p`. Variant Beaufort is covered
  by negating both the free base key and drift.
- Key: `k_i = B[i % m] + d * floor(i/m) (mod 26)`, every period m=1..24,
  every drift d=0..25, and arbitrary base-key values B. Phase zero represents all
  phases after relabeling and adjusting free B; verify this equivalence in controls.
- Direct alignment only. No permutations, insertions, deletions, alternative
  alphabet-building conventions, or other schedules.

## Exact test and interpretation

For two observed positions in the same residue, implied key values must differ by
`d * (floor(j/m)-floor(i/m))`. Solve the first congruence for every allowable drift,
then test all remaining repeated-residue congruences. This is an exact existential
test over every base key, not a sampling or language-score test. Cross-check the
optimized filter with an independent scalar enumeration over all 26 drifts.

Record first-block internal constraints and how many second-block positions share
a first-block residue. When first-block letters do not determine drift or a base
residue, identify that remaining freedom; do not describe all second-block letters
as independent predictions. Both public crib blocks are already known, so this is
not a genuinely blind external validation.

Report counts for every period/configuration/sign and all drifts, including zero.
Stored examples are capped at 100 per period/configuration/sign; the exact count
is never capped and every binding example cap is recorded. For each example record
alphabet provenance, drift, all constrained base values, unfilled residues, and
partial decryption. Validate all determined letters by forward encryption. Do not
invent missing base values just to produce a complete-looking message.

Any compatible output remains a fitted model. This experiment makes no automatic
solution decision from an English score and runs no base-key completion search.
A future solution claim would require coherent complete plaintext, all 97 forward
matches, and independent support for the key construction.

## Controls, order, and budget

1. Scalar enumeration cross-checks on random observed-key matrices.
2. Actual K1/K2 controls: recover KRYPTOS with zero drift at their known periods.
3. Thirty planted progressive instances spanning all six configurations, both
   signs, several periods, nonzero and zero drift, and nonzero phases. Recover the
   planted alphabet, period, and drift. Also verify a deterministic tampered
   observation rejects its original planted parameters.
4. Run K4 once.
5. Twelve fixed-seed permutations of K4's letters through the same complete
   filter. Report empirical counts; twelve samples cannot calibrate very small
   tail probabilities. Uniform-key expectations, if shown, are reference-model
   calculations only, not authenticated probabilities for keyword alphabets.

Seeds: controls 20261007; null permutations 20263007 through 20263018.
Use one CPU process, existing NumPy, under 20 minutes, and under 20 MB of output.
No network or downloads are part of the experiment. If a limit prevents completing
the declared scope, label it incomplete rather than claiming an exclusion.

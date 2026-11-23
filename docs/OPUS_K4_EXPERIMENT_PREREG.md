# Pre-registration: keyword-tableau K4 experiment (Opus review)

Written 2026-10-07 UTC, before any run of this family on the K4 ciphertext. The
SHA-256 of this file is recorded in the experiment output. Changes after the first
K4 run must be listed in the output's `deviations` field.

## Question

Is K4 a direct-alignment keyword-tableau substitution, of the kind Sanborn used for
K1/K2, with a dictionary-word alphabet and a low-entropy key schedule?

## Independent motivation (not derived from K4 outputs)

1. K1 and K2 decrypt as Quagmire III with the keyword alphabet KRYPTOS and keys
   PALIMPSEST (period 10) and ABSCISSA (period 8); reproduced in this repository.
2. Reported Sanborn statements: BERLINCLOCK "matches directly" one-to-one with
   NYPVTTMZFPK (B. Bogart, 2019, attributing it to Sanborn); BERLIN starts at
   exactly character 64 (K. Schmeh's notes). These support direct alignment.
3. Scheidt (2011, as reported by E. Hannon and cited by Bean 2021): K4 can be
   executed "when used with the correct key word/s".
4. Audit result: with keyed alphabets unknown, direct-alignment periods 8, 13,
   16, 19, 20, 23, 24 and 26 are crib-compatible. The repository tested only the
   ABC and KRYPTOS alphabets.
5. Bean (2021) proposed Gromark-type numeric keys with mixed alphabets.

## Family (fixed in advance)

- **Alphabets W.** Every entry of `/usr/share/dict/web2` (235,976 lines), plus the
  fixed Kryptos-context list in `research/opus_review/keyword_tableau.py`. Each
  word is turned into three alphabets: `kryptos` (deduplicated word, then the
  unused letters A–Z), `continue` (unused letters starting after the word's last
  letter) and `columnar` (the kryptos alphabet read by columns in key order). Duplicate
  alphabets are removed, keeping the first source.
- **Configurations.** Plaintext and ciphertext alphabets (W,W), (W,ABC), (ABC,W),
  (W,KA) and (KA,W). Pairs of distinct context words (W1,W2) are also included.
- **Sign conventions.** Vigenère c=p+k and Beaufort c=k−p (variant Beaufort, c=p−k,
  is equivalent to Vigenère for periodic keys). For numeric schedules, all three
  conventions are used.
- **Schedule S1, periodic.** k_i = x_(i mod p), p = 1..26, with x free. This is
  invariant under alphabet rotation.
- **Schedule S2, lagged Fibonacci (Gromark/Vimark).** k_i = k_(i−L) + k_(i−L+1)
  (mod b), L = 2..12, b = 2..26, used as shifts mod 26. All 26 alphabet rotation
  offsets are included.
- **Alignment.** Direct only: no transposition, nulls or deletions.

## Test

The 13 EASTNORTHEAST key values are fitted first. They are then used to predict the
11 BERLINCLOCK letters that the schedule determines. A survivor must reproduce every
determined crib letter exactly; no language score enters the test.

## Controls

- **PC1, positive and real.** Five 97-letter windows of Sanborn's K2, with K2
  plaintext cribs at the K4 crib offsets. The test must recover KRYPTOS, (W,W),
  Vigenère, period 8.
- **PC2, positive and real.** K1, with cribs at offsets 0–12 and 42–52. The test must
  recover KRYPTOS, (W,W), Vigenère, period 10.
- **PC3/PC4, positive and synthetic.** 30 planted S1 instances and 20 planted S2
  instances. Each has a random dictionary alphabet, configuration, sign and
  parameters, and uses K1–K3 plaintext windows with the K4 cribs inserted. The test
  must recover the planted cell.
- **NC, negative.** Random permutations of the K4 ciphertext letters, giving
  empirical survivor counts per cell. These are compared with the analytic
  expectation N_tests × 26^−checks.

## Acceptance rules (fixed in advance)

1. A K4 survivor is *reportable* only if its cell's expected false-survivor count
   is below 0.05. For other cells, only counts are reported.
2. A reportable survivor is a *candidate* only if every letter it determines reads
   as coherent English on inspection, and it scores above the 99th percentile of
   null-control decryptions.
3. A candidate is not a solution without all 97 letters, a reversible full
   regeneration, and keyword provenance independent of fitting K4. A dictionary
   hit alone is insufficient.
4. Every cell's counts are published, including empty ones and failures.

## Budget

One process, standard library plus numpy (already in `requirements.txt`), under
about 20 minutes total and under 50 MB of output. No network.

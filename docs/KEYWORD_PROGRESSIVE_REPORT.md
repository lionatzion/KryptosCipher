# K4: bounded keyword-tableau progressive-key experiment

2026-10-07. **No additional confirmed plaintext and no solution found.** The complete
registered search has no crib-compatible model at periods 1–23. Period 24 has six
fits in three alphabet/configuration cases, each with two drifts. Their determined
text is incoherent, and comparable fits occur in shuffled controls. This result
extends the earlier fixed-alphabet progressive search to the registered keyword
alphabet family; it does not eliminate all progressive or keyword-based ciphers.

## Design and exact scope

The [design](KEYWORD_PROGRESSIVE_PREREG.md) was recorded and hashed before execution.
SHA-256: `20b43f9b7e0d9b087d354ef123be241f346f0517351c9d05d3030bc84c311185`.
The same hash is stored before the run and embedded in the generated result.

This uses the canonical 97-character ciphertext and 24 public anchor letters.
The registered dictionary's SHA-256 is
`be41ad97963bf8dabedd5871d5d691596175269d540956b0f9965a885c2bbab9`.
It has 235,976 nonempty lines. Together with Opus's 74 context words and three
alphabet constructions, it produces **617,732 distinct alphabets**. The program
checks the dictionary hash and alphabet count before searching. It also records
the ordered-alphabet hash, Python version and NumPy version.

Plain/cipher alphabet configurations are W/W, W/ABC, ABC/W, W/KA, KA/W and the
46,440 ordered pairs of different context alphabets. W/W uses the same keyword
alphabet on both sides; arbitrary pairs of two dictionary keywords are not covered.

The key equation, using zero-based positions, is:

```text
k_i = B[i % m] + d * floor(i/m) mod 26
```

Every period m=1..24, every drift d=0..25, Vigenere and Beaufort signs, and arbitrary
base values B are covered. Variant Beaufort is equivalent here after negating B
and d. Phase changes are absorbed into a relabeling and adjustment of free B;
controls check this identity. No transposition or transcription change is included.

The search covers **6,270,200 alphabet/configuration/sign rows** and
**3,912,604,800 nominal row/period/drift tuples**. These are parameter counts,
not independent statistical trials. The base keys are tested for existence by exact
congruences rather than enumerated as full strings.

For any observed positions i,j in the same residue, their implied key difference
must equal `d*(floor(j/m)-floor(i/m)) mod 26`. The implementation solves one
congruence, retaining all roots even when its coefficient is noninvertible, then
checks the remaining repeated-residue constraints. An independent scalar version
enumerates all 26 drifts and fits base values directly for verification.

## Results

| Scope | K4 compatible parameter fits | Twelve shuffled controls |
|---|---|---|
| Periods 1–23, all registered alphabets and drifts | 0 | 0 |
| Period 24 | 6 | Mean 18; range 2–52 |

All six fits are retained; no example cap bound. All determine **77 letters**, of
which 24 are the supplied cribs. They leave base residues **10–14** free, causing
20 unknown plaintext positions. Each has 77/77 forward matches on its determined
letters. This is an internal consistency check, not full 97-letter verification.
No free base values were filled and no completion ranking was run.

| Keyword provenance | Alphabet construction | Plain/cipher configuration | Sign | Drifts |
|---|---|---|---|---|
| Mocoan | columnar | W/ABC | Beaufort | 3, 16 |
| catallactically | columnar | W/KA | Vigenere | 10, 23 |
| aguilarite | continue | KA/W | Beaufort | 1, 14 |

The source words identify the first dictionary entries generating the alphabets;
they are not independent evidence that Sanborn selected these words. All constraints
link positions separated by 48, so period 24 only observes `2*d mod 26`. The two
drifts in each case differ by 13 and are indistinguishable at the supplied crib
positions. Five base residues still allow 26^5 completions per parameter fit.

Representative determined text (drift 3, Mocoan alphabet):

```text
IKQSPRHTHF?????JNHEWJEASTNORTHEAST?????SLXLOKXZQOWOGSGOMNU?????BERLINCLOCKOIPOTTRR?????JAENVRMLSE
```

The other five outputs, alphabets and all constrained key values are in
[`result.json`](../out/keyword_progressive_20261007/result.json). Their fixed text
also provides no credible message. This is a practical language assessment, not a
formal impossibility proof for period 24.

Null period-24 counts are `8,12,14,20,16,16,2,52,16,18,10,32`. Six K4 fits are not
an excess over these controls. Twelve nulls are insufficient to calibrate small
tail probabilities; no significance level or breakthrough is claimed. The output
also contains an explicitly labeled uniform-independent-key reference expectation.
Keyword alphabets and repeated crib letters violate that reference model, so its
numbers are not authenticated probabilities.

## Controls and validation

- The optimized filter agrees with scalar enumeration on random matrices and on
  planted instances at every period, including noninvertible congruence cases.
- Six real-data controls recover KRYPTOS with zero drift: five K2 windows at period
  8 and K1 at period 10. Each is the unique compatible row/drift pair in its tested
  W/W Vigenere cell.
- Thirty synthetic plants spanning all six configurations and both signs are
  recovered by searching their full registered alphabet/configuration cell at the
  true period. Zero and nonzero drifts and nonzero phases are included. Each also
  passes full 97-character round-trip verification. Tampered observations reject
  the original planted parameters.
- Twelve fixed-seed ciphertext permutations pass through the same complete search.
- Three new tests check scalar agreement, phase equivalence and tampering. Together
  with Astra's and Opus's tests, the publication suite has 29 tests.

One logged validation change occurred after the first run: the initial synthetic
controls checked the planted alphabet row; the final run strengthened them to search
their complete configuration at the true period. The K4 search scope, filter, seeds
and interpretation did not change. The initial result and log are retained, and
the final run records this deviation. Both runs give the same K4 and null counts.

## Reproduce and limits

Use Python 3.10+ with NumPy and the registered dictionary bytes. No new dependency
was installed in this run. The existing environment was Python 3.13.5 and NumPy
2.1.3. The first complete run took 31.39 seconds in one CPU process; the strengthened
final run took 33.19 seconds. Output is small JSON plus logs.

```bash
python3 -m unittest discover -s tests -v
python3 -m research.keyword_progressive --outdir out/progressive_reproduction
# An equivalent dictionary file can be supplied with --dictionary PATH.
```

Default dictionary: `/usr/share/dict/web2`, available on this Mac. A matching
filename alone is insufficient: the SHA-256 must match. A different dictionary
requires a separately documented experiment. No dictionary is bundled or downloaded.

**Exact exclusions:** the enumerated alphabet constructions/configurations/signs
with this progressive equation at periods 1–23, under direct alignment.

**Still open:** the six incomplete period-24 fits, periods beyond 24, unlisted names
or phrases and non-English keyword sources, other alphabet conventions, arbitrary
dictionary-word pairs, autokey and other schedules, transcription changes and
transposition hybrids. Compatibility does not establish any of these as promising.

The next useful test would need a specific additional mechanism or independent
constraint. This run does not justify completing millions of arbitrary period-24
keys or reviving period-27 phase sweeps.

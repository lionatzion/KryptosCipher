# Kryptos K4: independent review of the Astra research

Opus 5.5, 2026-10-07 UTC. Local branch `research/opus-k4-review`, from
`183f1bfbcf4038b08290d63c288847c59dc201da`. Nothing was pushed, merged, or sent.

Publication note, 2026-10-07: the sentence above describes the original Opus run.
Codex subsequently verified all 26 tests, all 39 original manifest hashes, and the
complete keyword-periodic counts, then prepared this work for GitHub at Ryan's
request. This version qualifies the language and information estimates, distinguishes
arbitrary alphabets from dictionary alphabets, and corrects the K5 reuse inference.
The original numeric experiment outputs are retained. `manifest_original.json` records
the pre-publication files; the regenerated `manifest.json` covers the current review.
The failed-run traceback replaces its private checkout prefix with `<repository>`.
A publication manifest also records the new experiment and updated documents.
See [the new progressive-key experiment](KEYWORD_PROGRESSIVE_REPORT.md).

## Verdict

- **No solution was found.** No additional plaintext letter, candidate message, or
  mechanism was identified. The public anchors still fix 24 of 97 letters.
- **Astra's arithmetic holds up.** All six committed result files regenerate
  byte-for-byte. A separate implementation reproduces every count; its core does not
  import Astra's code, and Astra's code is used only for comparisons and planted
  attacks. Planted-solution attacks found no false elimination: 300
  each for recurrence, progressive and feedback keys, plus four complete running-key
  reruns.
- **The alphabet extension leaves more models open.** Astra explicitly restricted
  "Periods 1–25 fail" to its ABC/KRYPTOS systems. With two arbitrary unknown
  alphabets, direct-alignment periods **8, 13, 16,
  19, 20, 23, 24 and 26** remain compatible with the cribs. I constructed and
  verified an explicit example for each. These witnesses are fitted permutations,
  not demonstrated single-keyword alphabets of the K1/K2 construction.
- **Most surviving families are bookkeeping, not signal.** Period-26 progressive
  survival is the parity of a single difference. The feedback survivors are exactly
  the lags at which the cribs collide once or not at all.
- **Prior work was missing from the handoff.** Bean (HistoCrypt 2021) had already
  derived the alphabet-free crib constraints, argued statistically against a
  transposition stage, and exhausted base-10 Gromark keys. My solver reproduces his
  published primer counts exactly (39, 4 and 3).
- **The archive establishes existence, not public recoverability.** A written method
  and the plaintext reportedly exist and are privately held. This source check did
  not locate an authenticated public full mechanism.
- **Alphabet assumptions change rejection rates.** Under this review's sampled
  random-key model, the rejection rate corresponds to about 113 bits for a known
  tableau and 11 bits for arbitrary unknown alphabets. These are model-dependent
  figures, not universal information budgets or guarantees for every key family.
- **Pre-registered experiment: null.** I tested 617,732 dictionary and context keyword
  alphabets in six tableau configurations, with Vigenère and Beaufort conventions. No
  periodic key of period 1–24, and no Gromark-type lagged-Fibonacci key (lags 2–12,
  bases 2–26), is consistent with the cribs. Sanborn's own K1 and K2, and all 50
  planted ciphers, were recovered. This excludes the registered dictionary,
  alphabet constructions, configurations and schedules within their tested bounds.

## 1. Scope and method

I read the handoff, the Astra report, `NEXT_STEPS.md`, `research/k4_core.py`,
`research/run_astra.py`, the tests, the legacy sweep and the manifests. I changed
no existing file. All new work is under `research/opus_review/`,
`tests/test_opus_review.py`, this document, the pre-registration
(`docs/OPUS_K4_EXPERIMENT_PREREG.md`) and `out/opus_review_20261007/`.

The environment was macOS 26.6.2 on arm64, Python 3.13.5 and numpy 2.1.3 (numpy is
already listed in `requirements.txt`). Everything ran in one process with no
accelerator. No model API is called by any script.

Web use was limited to reading public pages, listed under Sources. I read Bean's
paper in full from its open-access PDF. Two sources failed: the DocumentCloud scan
of Sanborn's letter returned HTTP 403, and a June 2026 explainer returned 404. They
are not treated as read. I ignored unverified "reconstructed plaintext" sites.

## 2. Audit

### 2.1 Reproduction

| Check | Result |
|---|---|
| Astra's 13 tests | Pass |
| `python3 -m research.run_astra` | 19.3 s; all six JSON outputs **byte-identical** to the committed files |
| Legacy period-27 baseline | 17,576 candidates; best −47.6380, key `YYGCKAZABMUYKLGKORNAIBLZCDC`; JSON identical |

The reproduced files are in `out/opus_review_20261007/reproduction/`.

### 2.2 Claim-by-claim check

| Astra claim | Independent check | Verdict |
|---|---|---|
| Input, SHA-256 and crib alignment | Recomputed; ABC Vigenère keys `BLZCDCYYGCKAZ` / `MUYKLGKORNA`; IC = 7/194 = 0.03608; all 26 letters occur | Confirmed |
| Period 27: zero checks, unknown residues 7, 8, 20, 86 forced letters | Template and forced text recomputed and matched character for character | Confirmed |
| Compatible periods for each of the 48 systems | Recomputed for periods 1–52 | Confirmed, **zero disagreements** (scope: those 48 systems) |
| Progressive keys: 438,048 tuples, 1,248 compatible | Recomputed; a parity rule predicts exactly 1,248 | Confirmed; reinterpreted (§2.3.2) |
| Feedback: 19,968 tuples, 1,298 compatible | Recomputed per lag | Confirmed; reinterpreted |
| Recurrence: 384 cases eliminated | Split by CRT. Brute force mod 2 (every order) and mod 13 (orders ≤ 4); my own GF(13) elimination for orders 5–8 | Confirmed. Every case fails mod 2 **and** mod 13 separately |
| Running keys: 11,980,800 tuples, 0 hits, best 8/24 | Recomputed from the same transcribed ciphertexts; K1/K2 plaintexts re-derived and checked | Confirmed |
| Not tested: corrected K2, K3 plaintext | **Closed here.** Corrected K2 text and ciphertext, K3 plaintext and concatenations: 13,049,088 tuples | 0 hits, best 8/24 |
| Legacy exports: 150 rows need phase 0, 110 need phase 26 | Replayed with my own decryption | Confirmed |
| Scoring excludes crib letters and windows touching cribs | Code reading and Astra's test | Confirmed |
| Soundness of the eliminations | Planted members of each family, run through Astra's own checkers | **0 false rejections**; no recurrence plant hit the cap |

To close the K2 gap I needed the corrected K2. Searching single-letter insertions
finds exactly one that turns `…WESTIDBYROWS` into `…WESTXLAYERTWO`: an **S** at 0-based
position 361. This independently confirms Sanborn's 2006 correction.

K3's plaintext was recovered by searching grid-rotation transpositions. The unique
output is the known K3 text, through equivalent width pairs such as 24 then 8,
rotated clockwise twice.

### 2.3 Corrections and qualifications

**1. Period eliminations depend on the alphabets assumed.** Bean's alphabet-free
argument applies to any cipher in which each position is enciphered by a bijection
selected by a key value:

- **Inequalities.** Same plaintext with different ciphertext, or the reverse, forces
  different keys. There are 22 such pairs, at differences 1, 3, 4, 5, 7, 9, 34, 42,
  43, 45 and 50.
- **Equality.** An identical pair forces equal keys whenever the tableau is a Latin
  square. The cribs contain one: positions 28 and 66, plaintext R to ciphertext P.

Applying these at every period gives (`audit/period_ladder.json`):

| Alphabet assumption (direct alignment) | Periods ≤ 26 still compatible |
|---|---|
| Astra's 48 fixed ABC/KRYPTOS systems | 26 only, in 2 systems |
| A different, unrelated alphabet for each residue | 8, 11, 12, 13, 16, 18, 19, 20, 22, 23, 24, 26 |
| Rows of one unknown Latin-square tableau | 8, 13, 16, 19, 20, 23, 24, 26 |
| Keyed Vigenère/Beaufort/Quagmire I–IV, alphabets unknown | 8, 13, 16, 19, 20, 23, 24, 26, each with an explicit verified construction |

For the Latin-square model, at most 24 cells are filled, fewer than the order 26. A
consistent partial square therefore always completes (Evans' conjecture, proved by
Smetaniuk in 1981), so this row is exact.

The keyed-tableau row was decided by an exact solver for c(C) = p(P) + k with unknown
bijections p and c. It returns either an explicit construction, checked by
re-enciphering the cribs, or an algebraic proof of impossibility. No period was left
undecided. The solver also reproduces Bean's Gromark counts, which validates it
against an independent published derivation (Gröbner bases in SageMath).

The repository's "Dead-ends: final-layer periods 2–26" should therefore read *for
the ABC and KRYPTOS alphabets*. Here is the period-8 construction the solver found:

```text
plain alphabet  DFGJRMPQUNOVSLEAKCBWXYHIZT   cipher alphabet FVRMAKBCNDEHTISJYOUPWZGLQX
residue keys    2 15 14 15 3 12 8 16
decryption      ACCLAMCFXHRUJGNQVVBCCEASTNORTHEASTJICDKZLNDTQWLMBAZDGVOWVAPZMEZBERLINCLOCKPQPWLNODWXOOIGNJKJQWTED
```

It contains every anchor and regenerates all 97 ciphertext letters, yet it is
gibberish. This is a concrete demonstration that a crib match plus a round trip is
not evidence.

**2. Most survivors carry essentially no information.**

- **Progressive keys at m = 26.** The only repeated residue is the pair of positions
  22 and 74. Compatibility therefore reduces to whether K74 − K22 is even.
  Same-alphabet systems always give an odd difference, because E and F are adjacent
  in both ABC and KA and the multiplier is odd. All 24 mixed-alphabet systems happen
  to give an even difference. The two zero-drift families are the cases where the
  difference is 0 mod 26.
- **Feedback lags.** Each residue chain modulo the lag is fixed by any crib inside it.
  Lags 27–29 contain no chain with two cribs, and lags 26 and 30 contain exactly one.

**3. Gromark keys were outside Astra's recurrence family.** Astra's recurrences work
modulo 26. Gromark uses digits modulo 10 (or another base), applied as shifts. Bean
covered base 10 and base 8 with arbitrary alphabets; I reproduce his 39 base-10
five-digit primers (including 26717, 84393 and 98800), the 4 base-8 primers, and the
three base-10 four-digit primers 3301, 6740 and 9903. My experiment's S2 arm covers
the standard expansion rule under keyword alphabets for bases 2–26.

**4. English running keys under the standard tableaux score poorly in this model.**
Under a known tableau, the 13 key letters at positions 22–34 would
themselves be consecutive key text. I tested 24 combinations:

- plaintext and ciphertext alphabets ABC or KRYPTOS (four pairs);
- Vigenère, Beaufort or variant Beaufort;
- key letters indexed in ABC or KRYPTOS.

Every 13-letter fragment scores at or below the **0.62nd percentile** of held-out
English windows, in either reading direction. A planted control with a genuine
English key scores at the 81st percentile. The largest product of the two marginal
tail fractions is 3.9×10⁻⁵. This product is not a calibrated joint p-value: dependence
between fragments and the choice of thresholds were not modeled.

This is a heuristic result: it uses a trigram model trained on Python's bundled
reference text. It does not eliminate every English source. The stored JSON's
`max_joint_tail_probability_either_direction` is a legacy field name for the product
described above, not an established joint probability. It says nothing about
keyword-mixed tableaux, where the fragment letters are unknown.

**5. The archive's "scrambled" text was not a cipher stage.** RR Auction describes
plaintext sentences that Sanborn cut into strips and taped out of order. They were
shown to the CIA's history staff and later turned up in the Smithsonian papers. This
is not evidence of a transposition layer.

**6. Priority 2 of the old plan (transposition) runs against the reported record.**
- Bob Bogart (2019) relays Sanborn's description of BERLINCLOCK → NYPVTTMZFPK as a
  direct one-to-one encipherment.
- Klaus Schmeh's notes record Sanborn confirming that BERLIN starts at exactly
  character 64 and that K4 is exactly 97 characters.
- Bean's permutation statistics point the same way.

None of this excludes a transposition, but it should not be the second priority.

**7. Priority 1 (World Clock labels as key material) is not what the letter
supports.** As quoted, the letter identifies the World Clock as the place the
plaintext refers to: the gathering point at the fall of the Wall. That concerns the
message's meaning, not its key. A clock-derived key remains testable, but its
extraction rules are unbounded and it lacks independent support.

**8. A transcription error, like K2's, does not rescue the simple families.** The
sculpture omits one letter in K2. I shifted BERLINCLOCK's key index by ±1, ±2 and ±3,
as if K4 had a net omission or insertion between the blocks
(`audit/transcription_shift.json`). The 48 fixed systems then have no periodic
survivor up to period 24, and the twelve sculpture running-key streams give zero
24/24 hits. This check is exploratory and was not pre-registered.

**9. Two statistics are weaker than they look.**
- **IC.** K4's IC of 0.0361 is a 4.4th-percentile event for period 8, a 14th for
  period 24, and a 22nd with no repetition (i.i.d. English letters). It is mild
  evidence against short periods only.
- **Width-21 bigram repeats.** Bean's 11 repeats at width 21 have p ≈ 0.0003 for that
  width alone. Correcting for having scanned widths 1–48 gives p ≈ 0.014, and other
  statistics examined over the years would weaken it further.

**10. Code defects.** I found none in Astra's code that change a result. Its scope
statements are accurate; the issue is how far the conclusions were generalized.

## 3. Progress, the archive, and identifiability

### 3.1 Has decipherment progressed?

Not in the sense that matters: no plaintext or mechanism has been recovered. The real
progress is methodological:
- an unsupported period-27 premise was removed;
- the computations are now reproducible;
- several explicit families are excluded within exact limits;
- with this review, it is now quantified *why* crib tests have been so weak.

The plaintext itself is no longer unknown to everyone. In 2025 Kobek and Byrne
reconstructed it from archived strips, Sanborn confirmed it, and it remains
unpublished. Public "decipherment" is now a question of recovering the method. If the
plaintext is ever published, that becomes a 97-letter known-plaintext problem,
dramatically easier than today's 24.

### 3.2 What the archive sale establishes

The first-party record shows the following.

- **Lot contents.** The lot comprises the handwritten K4 plaintext, the original K4
  coding system, the K1–K3 coding charts, a 1988 alternate K1, and a 1988 alternate
  K4 plaintext and chart now called K5. It also includes the plaintext used to cut
  the sculpture's screens.
- **No images.** RR Auction withheld photographs of those items, citing secrecy.
- **Sale.** It sold for $962,500 to an anonymous buyer, together with a private
  session with Sanborn.
- **The Smithsonian find.** It consisted of five pages of plaintext strips. Sanborn's
  own summary: "The scrambled plain text was found, but without the coding method or
  the key."
- **Sealing.** The Smithsonian files are reportedly sealed until 2075 (secondary
  source).
- **K5.** As quoted from his open letter, K5 will use a similar cryptographic system
  to K4, with BERLINCLOCK in the same position, and will be revealed after K4.

What this establishes:
1. A documented method existed in 1988–90 and still exists.
2. Sanborn distinguishes a *method* from a *key*, which suggests a keyed procedure,
   though not its entropy.
3. The answer is checkable in principle by the people who hold it.

It does **not** establish that the public ciphertext and clues determine the method.
It also discloses no detail of the method.

### 3.3 Could the public problem be underdetermined?

**Yes, possibly. It is not established, and the current hypothesis space certainly is
underdetermined by the cribs alone.** The 24 cribs carry 24 × log₂26 = 112.8 bits.
How much of that tests the key schedule depends on what is assumed about the
alphabets (`audit/identifiability.json`, 200,000 samples):

| Alphabet assumption | Fraction of random key schedules passing the cribs | Bits about the schedule |
|---|---|---|
| Tableau known (e.g. KRYPTOS) | 26⁻²⁴ | 112.8 |
| Keyed Vigenère/Quagmire, alphabets unknown | 4.4×10⁻⁴ | 11.2 (Bean's Gromark ratio 39/99,999 gives 11.3) |
| One unknown Latin square | 1.7×10⁻² | 5.9 |
| Unrelated alphabet per key value | 0.42 | 1.3 |

Under the sampled model, allowing free alphabets greatly increases the chance of a
compatible schedule. A family sampling that same distribution would have expected
compatible counts proportional to its size. This does not guarantee a survivor in
every family larger than 2¹¹: structured schedule distributions may behave differently.
Period 8 alone has 26⁸ ≈ 2³⁸ keys.

That is a statement about *these hypotheses*, not about K4. The other 73 letters must
also be English. With a strong language model that is worth roughly 3 bits a letter,
or about 200 bits, which is enough in principle to single out a low-entropy mechanism
(keyword alphabets of about 19 bits each, plus a keyword key). For K1/K2-like
mechanisms, then, the public data are probably sufficient in information terms, and
the obstacles are search over unknown families and unreliable scoring of short
texts.

If instead the coding system includes a per-message table, such as a random key or
position-specific alphabets, its description length exceeds what 97 letters can
determine, and public cryptanalysis cannot recover it.

The evidence leans toward low entropy, without establishing it:
- **For a keyed, low-entropy method:** K1–K3 practice; Scheidt's reported remark that
  K4 can be executed with the correct key word or words; the fact that Sanborn
  released cribs at all, which would be useless against a one-time key; and his
  method/key distinction.
- **Pointing the other way:** the auction's "chart" vocabulary for K4 and K5, and 35
  years of failure.

## 4. Ledger

**Proven** by exact computation, with the tests listed:

- Canonical input, crib alignment and IC; self-encryption at positions 33 and 74.
- The alphabet-free relations: one equality and 22 inequalities, with the
  period-by-period consequences in the table in §2.3.1.
- Explicit crib-compatible keyed-tableau constructions at periods 8, 13, 16, 19, 20,
  23, 24 and 26. They regenerate 97/97 letters, so round trips are not evidence.
- Every Astra elimination within its stated scope.
- Bean's Gromark counts, reproduced exactly.
- K2's single-letter correction and the K3 transposition. These are positive
  controls on Sanborn's own ciphers.

**Eliminated within exact scope** (new here):

- Running keys from the corrected K2 text and ciphertext, the K3 plaintext and their
  concatenations, under the 48 systems.
- The pre-registered experiment (§6) found zero survivors for the keyword-mixed
  tableaux. That covers 617,732 alphabets in five configurations plus context-word
  pairs, under Vigenère and Beaufort, with two key schedules:
  - periodic keys of period 1–24;
  - lagged-Fibonacci keys with lags 2–12 and bases 2–26, at every offset, under three
    sign conventions.

  The expected chance survivors are below 10⁻³ in each reported cell.
- *Exploratory:* a ±1 to ±3 index shift between the blocks, for the 48-system periodic
  family (p ≤ 24) and the twelve sculpture streams.
- *Heuristic evidence only, not an elimination:* poor language scores for the forced
  key fragments under 24 tableau/sign/indexing combinations, in either direction.

**Speculative**, with my weighting:

| Hypothesis | Weight | Basis |
|---|---|---|
| Direct alignment | Moderately supported | Sanborn statements via Bogart and Schmeh; Bean's statistics |
| A keyword-based key | Weakly supported | Scheidt's reported remark |
| Gromark-type numeric keys | Weakly supported | Flat IC; Bean |
| A width-21 structure | Weak | Scan-corrected p ≈ 0.014 |
| A transposition stage | Disfavoured | Statements and statistics in §2.3.6 |
| World Clock key material | Unsupported | The letter concerns meaning |

**Open:** which alphabets or tableau K4 uses; the key schedule; the entropy of the
coding system; whether the sculpture's K4 contains a copying error; the 73
unconfirmed letters; and how K4 relates to K5.

## 5. Three ranked approaches

All three assume direct alignment. Each fits on EASTNORTHEAST, predicts BERLINCLOCK,
and is run against shuffled-ciphertext nulls and planted controls. Sanborn's real K1
and K2 serve as positive controls.

### 1. Keyed tableau with a pre-declared key source

- **Evidence.** K1 and K2 are exactly this construction. Tests limited to ABC/KA
  alphabets leave keyed tableaux open at eight periods (§2.3.1). Scheidt's reported
  remark refers to key words.
- **What is already done.** §6 excludes periodic and standard Gromark schedules under
  dictionary keyword alphabets. The next step is the remaining low-entropy key
  sources, listed below.
- **Mechanism and inverse.** c(C_i) = p(P_i) + k_i, or the Beaufort forms, with p and
  c taken from keyword alphabets, ABC or KRYPTOS. The inverse is subtraction in the
  same tableau.
- **Key sources.**
  - plaintext or ciphertext autokey with a keyword primer;
  - progressive keys;
  - clock-arithmetic steps modulo 12 or 24;
  - running text from a short, pre-declared list of public-domain sources tied to the
    plaintext's stated inspirations, e.g. Carter's 1923 Tutankhamun account, which is
    K3's source.
- **Free parameters.** Keyword (about 19 bits), configuration and sign (about 3 bits),
  source offset (10–17 bits) and direction (1 bit).
- **Cheap falsifier.** A fully determined schedule predicts all 11 block-2 letters.
  The expected false survivors are about 6×10⁶ × 26⁻¹¹ ≈ 10⁻⁹ per schedule.
- **Missing inputs.** The texts, which are small public-domain downloads needing
  Ryan's approval.
- **Budget.** Minutes per source. The `keyword_tableau` engine already supports this.

### 2. Calibrated cryptodiagnosis to choose families before searching keys

- **Evidence.** K4's ciphertext statistics are independent of the cribs: the IC of
  0.0361, the width-21 repeats, and the "minor differences" Bean reports.
- **Method.** Simulate each candidate family on English plaintext, including the
  keyed tableau with periodic, autokey, running and Gromark keys of several bases, and
  any transposition hybrid someone wants to defend. Estimate the likelihood of K4's
  *pre-registered* summary statistics under each, correcting for scanning widths and
  statistics.
- **Free parameters.** The family set and the statistics, both declared before
  looking at the results.
- **Falsifier.** A family under which K4's statistics fall below the 1% level is
  deprioritized.
- **Controls.** Statistics computed on K1–K3 and on synthetic ciphertexts.
- **Budget.** Minutes.
- **Value.** It turns intuition, such as "Gromark explains width 21", into measured
  likelihood ratios. The width-21 anomaly shrinks from 1 in 3,300 to about 1 in 70 once
  the width scan is counted.

### 3. Generalized numeric key generators

- **Evidence.** Bean's diagnosis, Gillogly's earlier suggestion, the flat IC, and
  Scheidt's remarks about changing the language "base". The Berlin clocks' base
  arithmetic is weak support.
- **Mechanism.** Linear recurrences with 0/1 taps up to order 12 modulo b = 2..26,
  applied as shifts in keyword or arbitrary alphabets. My S2 arm covers only the
  standard rule k_i = k_(i−L) + k_(i−L+1).
- **Falsifier.**
  - Keyword alphabets: the block-1 fit predicts block 2.
  - Arbitrary alphabets: the exact Quagmire solver, which is worth only about 11 bits.
    Survivors must then beat a calibrated null on the other 73 letters, which is the
    overfitting zone, so only keyword alphabets give decisive tests.
- **Budget.** Minutes.

**Demoted:** World Clock label keys (§2.3.7), transposition hybrids (§2.3.6), and any
further period-27 completion or phase sweep.

## 6. Executed experiment (pre-registered)

### Question

Is K4 the K1/K2 construction (a keyword-mixed tableau with direct alignment) using a
different dictionary keyword and a low-entropy key schedule?

### Pre-registration and deviation

The design is in `docs/OPUS_K4_EXPERIMENT_PREREG.md`. Its SHA-256 (`8c832755…e6a1`)
was recorded at 05:28 UTC, before any run on K4.

There was one deviation, logged in the output. The first K4 run crashed on a
variable-shadowing bug before it wrote or printed anything. I renamed the variable
and reran; no family, control or rule changed.

### Family

- **Alphabets.** 617,732 distinct alphabets: every entry in `/usr/share/dict/web2`
  (235,976) plus 74 pre-declared context words, each built three ways.
- **Configurations.** Plaintext/ciphertext alphabet pairs (W,W), (W,ABC), (ABC,W),
  (W,KA) and (KA,W), plus 46,440 ordered pairs of distinct context alphabets.
- **Periodic schedule (S1).** Periods 1–26, Vigenère and Beaufort: 6,270,200 rows
  tested per period.
- **Lagged-Fibonacci schedule (S2).** Lags 2–12, bases 2–26, all 26 offsets and three
  sign conventions: 9,405,300 rows, or about 6.7×10¹⁰ schedule tests.

Each candidate is fitted on EASTNORTHEAST and must predict BERLINCLOCK exactly.

### Controls

| Control | Result |
|---|---|
| Sanborn's K2, five 97-letter windows (KRYPTOS, period 8) | Recovered 5/5; each time the only period-8 survivor among 617,732 alphabets in the (W,W) Vigenère configuration |
| Sanborn's K1 (KRYPTOS, period 10) | Recovered; the only period-10 survivor in the same configuration |
| 30 planted periodic ciphers (random keyword, configuration, sign, period) | 30/30 recovered |
| 20 planted lagged-Fibonacci ciphers | 20/20 recovered |
| 40 shuffled-ciphertext nulls (S1) and 10 (S2) | No survivor in any reportable cell; no S2 survivor |

### K4 results

| Period | Fit → predict checks | Expected chance survivors | K4 survivors | Mean in nulls |
|---|---|---|---|---|
| 1–14 | 23 down to 11 | ≤ 2×10⁻⁹ | 0 | 0 |
| 15, 19, 22 | 9 | 1×10⁻⁶ | 0 | 0 |
| 16 | 8 | 3×10⁻⁵ | 0 | 0 |
| 17, 18, 23 | 7 | 8×10⁻⁴ | 0 | 0 |
| 20, 21 | 11 | 2×10⁻⁹ | 0 | 0 |
| 24 (weak cell) | 5 | 0.53 | 0 | 0.33 |
| 25 | 3 | 357 | 0 (forced: the 22/72 inequality defeats every alphabet) | 405 |
| 26 | 1 | 241,162 | 220,824 | 220,328 |
| S2, all lags and bases | ≥ 11 | 7×10⁻⁹ | 0 | 0 |

### Interpretation

The alphabet-free ladder (§2.3.1) shows that periods 8, 13, 16, 19, 20, 23 and 24 are
open for *some* pair of alphabets. This experiment shows that the required alphabets
are not dictionary keyword alphabets in these constructions and configurations. In
other words, K4 is not "K1/K2 with a different dictionary word and a period up to 24",
nor that construction with a standard Gromark/Vimark expansion.

Period 26 survivors appear at exactly the null rate. They carry no information and
were not examined as candidates, as the acceptance rules required. With no reportable
survivor, acceptance rule 2 (the English-score gate) never came into play. The JSON
still records the null score distribution, drawn from K4's weak-cell fits.

### Not excluded

- keywords that are phrases, names missing from web2, or non-English words;
- other alphabet constructions;
- two unrelated dictionary keywords (Quagmire IV beyond the context pairs);
- the fourth Beaufort sign convention in S2;
- non-periodic schedules other than standard Gromark;
- transposition hybrids;
- copying errors.

### Resources

535 s in one process; peak memory footprint 0.39 GB (maximum resident set 1.06 GB);
the JSON output is 49 KB. To reproduce:

```bash
python3 -m research.opus_review.run --only experiment
```

## 7. The most valuable next constraint

**The identity of K4's substitution alphabets.** Knowing a tableau fixes the 24
implied key values and can strengthen tests of a specified schedule. The 11/113-bit
comparison applies to the sampling model in §3.3; actual independent checks depend
on the schedule. A freely fitted period-27 key would still have zero repeat checks.
Three possible sources of additional constraints are:

- an authorized yes/no on whether K4 uses the KRYPTOS tableau on the sculpture;
- an authenticated image of a coding chart;
- K5 itself.

**K5 is the most valuable single observation.** Sanborn says it uses a similar system
with BERLINCLOCK in the same place. That gives a ready, cheap falsifier: if K4 and K5
share a position-indexed keystream and tableau, K5's letters 64–74 must read
`NYPVTTMZFPK`.
- If they do, it supports reuse at those eleven positions. It does not prove shared
  alphabets and keystream throughout both messages. Cancellation across the entire
  texts would require that stronger reuse assumption to be independently established.
- If they do not, the identical-tableau/identical-keystream hypothesis fails at those
  positions. A similar cipher system with a different key or state remains possible.
  Joint analysis would require an explicit, testable shared-parameter hypothesis.

After that, any additional authenticated plaintext letters between positions 35 and
63 would help most, because they would link the two crib blocks for every
position-indexed key.

I did not contact anyone. Whether to seek any of this is Ryan's decision.

## 8. Reproduce

```bash
python3 -m unittest discover -s tests -v                 # 13 Astra tests + 13 review tests
python3 -m research.run_astra --outdir out/opus_review_20261007/reproduction
python3 -m research.opus_review.run                      # all audit tasks, then the experiment
python3 -m research.opus_review.run --only period_ladder # or any single task
python3 -m research.opus_review.run --only manifest      # file hashes and environment
```

All outputs are in `out/opus_review_20261007/`:

| Path | Contents |
|---|---|
| `reproduction/` | Astra's rerun and test log |
| `audit/*.json` | One file per audit task |
| `experiment/keyword_tableau.json` | The experiment, including controls, nulls and deviations |
| `experiment/prereg_hash_before_k4_run.txt` | Pre-registration hash, recorded before any K4 run |
| `experiment/failed_first_attempt_*` | Logs of the crashed first run |
| `manifest.json` | Hashes and environment |

## 9. Limitations

- **Direct alignment** is assumed throughout, except for the shift check in §2.3.8.
- **Language judgments are heuristic.** They use a trigram model built from Python's
  bundled reference text, and an i.i.d. letter model for the IC.
- **Monte Carlo figures carry sampling error**, as stated in each JSON file.
- **Experiment family limits.**
  - Keywords are drawn from one English dictionary plus a 74-word context list; the
    alphabet constructions follow three conventions; and Quagmire IV pairs use only
    context words.
  - S2 covers three sign conventions. The fourth, k = −(c + p), arises only for
    reversed alphabets under Beaufort and is not covered.
- **Sanborn's and Scheidt's statements** were read through secondary reports. The
  letter scan was not accessible.

## Sources

- R. Bean, [Cryptodiagnosis of "Kryptos K4"](https://ecp.ep.liu.se/index.php/histocrypt/article/view/153), HistoCrypt 2021 (read in full).
- RR Auction, [K4 discovered, not solved](https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/) (2025-10-23); [archive sale](https://content.rrauction.com/jim-sanborns-complete-kryptos-archive-sells-for-962500-at-auction/) (2025-11-21); [lot description](https://www.rrauction.com/jim-sanborn-kryptos-k4-solution-auction/).
- AFP via [eNCA](https://www.enca.com/lifestyle/auction-famed-cia-cipher-shaken-after-archive-reveals-code) (2025-11-19): Sanborn on the scrambled plaintext without method or key.
- Popular Mechanics via [AOL](https://www.aol.com/articles/cia-home-unsolved-puzzle-35-130000201.html) (2025-11-19): quotations from Sanborn's open letter (World Clock, K5). The primary scan returned 403.
- B. Bogart's comment on K. Schmeh's [CNN documentary report](https://scienceblogs.de/klausis-krypto-kolumne/2019/03/15/cnn-documentary-about-kryptos-a-making-of-report-with-many-photographs/) (2019), and Schmeh's notes there.
- [Wikipedia: Kryptos](https://en.wikipedia.org/wiki/Kryptos), checked 2026-10-07: no public disclosure of the plaintext or method; files sealed until 2075.

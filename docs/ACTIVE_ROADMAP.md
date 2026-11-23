# Active research roadmap

Refinement dated November 23, 2026. These are three proposed experiments, not
executed campaigns or new exclusions. Freeze each experiment's equations,
inputs, code hash, budget and controls before inspecting its K4 results.

## 1. Bounded base-10 keyword Gromark

**Question:** Can a dictionary-derived ciphertext alphabet and a five-digit
base-10 recurrence fit the anchors with one arbitrary plaintext alphabet?

- Register a legally usable wordlist, its exact bytes, normalization rules and
  thematic additions. Hash both the input and the ordered deduplicated alphabet
  list. An English wordlist constrains keys, not the language of the plaintext.
- State the equation as `index_CT(C[i]) = M(P[i]) + sign*k[i] (mod 26)`, with
  sign in `{+1,-1}`, M an injective plaintext-letter mapping, and
  `k[i]=(k[i-5]+k[i-4]) mod 10`. Exhaust all 100,000 primers including leading
  zeros. Any alphabet rotation or starting offset must be registered explicitly.
- For each repeated anchor plaintext letter, the shortest circular arc containing
  its ciphertext indices must span at most **9 steps**. This is necessary for
  digits 0..9 under this equation, not a sufficient solution test.
- Check equal plaintext letters require equal M values, and different letters
  require different M values. A partial injection extends to a full permutation,
  so existence can be checked without literal enumeration of 26! alphabets.
  Unobserved mappings remain unknown; do not fill them arbitrarily to score text.
- Before running, compare the scope with
  [October S2](OPUS_K4_EXPERIMENT_PREREG.md). That campaign used fixed dictionary
  alphabet pairs, ABC/KRYPTOS combinations, and pairs of context alphabets.
  Allowing **any** plaintext alphabet for each dictionary ciphertext alphabet
  expands that scope. Dictionary-versus-dictionary overlap must be identified,
  not counted again as independent evidence.
- Require planted recoveries, a scalar/vectorized cross-check, tampering tests,
  exact survivor records and identical-budget random controls. Save any cap as
  an incomplete search. Do not promise the full campaign will take minutes.

The span filter already uses both cribs. A later BERLINCLOCK check is therefore a
withheld fitting check, not untouched validation. A hit identifies a compatible
model; it does not by itself identify every plaintext letter or prove K4 solved.

## 2. Independently specified alternating-parity generators

**Question:** Does a small, independently motivated key generator explain the
observed pairwise parity relation and the ciphertext beyond the fitted cribs?

- Specify generator equations, allowed parameter values and alphabet mapping
  before searching. Free shifts at every position are not an explanatory model.
- Treat globally alternating key parity as one hypothesis. The observed
  repeated-letter relation does not establish it. Do not ban shift then substitute
  without the universal-key assumption required by the stronger order theorem.
- Demonstrate recovery on novel seeded plaintext/key instances and rejection of
  tampered cases. Bound every free alphabet value and generator parameter.
- Report 64 unknown-only and 12 boundary quadgram scores separately, with the
  corpus hash and full-pipeline controls. Do not use the earlier -5.20 threshold
  on a different scorer. Show a comparison branch without the parity assumption.

Conditional on a completely specified substitution and parity rule, parity may
leave 13 letter choices at a position. The observed crib partition alone does
not supply that complete rule or recover unknown letters.

## 3. Masking and rearrangements beyond a constant phase change

**Question:** Can a reversible physical or positional rule produce a genuinely
different correspondence from a simple gap between intact crib blocks?

- Retain disrupted routes, interrupted key advances and measured sculpture
  alignments as hypotheses. Define gather permutations, null positions, key
  advancement and inverse reconstruction exactly. Preserve the confirmed cribs.
- A **key-index skip inside an anchor span** may interrupt the schedule while
  retaining each public plaintext/ciphertext pair. A **ciphertext null at a
  confirmed anchor position** removes a known correspondence and contradicts the
  current direct anchor model. Do not quietly treat these as the same operation.
  Any alternative alignment requires an explicit, justified mapping back to the
  original positions and synthetic controls validating that mapping.
- Record YAR/extra-L coordinates, front/back orientation, units and measurement
  uncertainty. If using clock cities or bearings, document the historical list,
  source date, origin and rounding convention. Do not invent an official city ring.
- Prove the proposed rule cannot be reduced to a single relative phase shift.
  Such shifts already fail periods 1–23 in the tested STD/KRYPTOS models with
  intact crib blocks, regardless of gap length. The old period 1–16 gap-null
  campaign is retired.
- Keep unassigned key residues explicit and retain valid sparse-collision
  constructions. Compare the complete registered search against matched controls.

## Shared reporting contract

The existing [ledger](HYPOTHESIS_LEDGER.json) keeps **status** separate from
**evidence type**. Gemini's four proposed labels map as follows:

| Proposed evidence label | Existing representation |
|---|---|
| `exact_contradiction` | `status=eliminated`, `evidence_type=exact_conflict` |
| `exhaustive_bounded_search` | `status=eliminated`, `evidence_type=exhaustive_bounded` |
| `heuristic_rejection` | `status=sampled_null` or `statistical`, with the actual scoring evidence and limits |
| `reported_unverified` | `status=unverified`, `evidence_type=reported_only` |

Retain `open` and `retired` for proposals and withdrawn interpretations. A score
rejection is not an exact impossibility proof. The reported 61.8 million campaign
remains unverified locally. No candidate is sent to a paid verifier by these plans.

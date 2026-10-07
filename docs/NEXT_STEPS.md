# K4: what changed and what to test next

Research status, 2026-10-07: **no additional confirmed plaintext recovered**.
The public anchors still account for 24 of 97 characters. Our work corrected
unsupported assumptions, repaired reproducibility problems, and excluded specific
algebraic families. It did not establish a candidate message or key.

## What the archive sale means

According to [RR Auction's November 2025 announcement](https://content.rrauction.com/jim-sanborns-complete-kryptos-archive-sells-for-962500-at-auction/),
the sold archive includes K4's handwritten plaintext and original coding system.
Those are the artifacts needed to explain the cipher, not merely another public
hint or a password. The buyer was anonymous in that announcement. This source
check did not locate an authenticated public disclosure of the complete method.

The archive's existence supports the claim that a construction and explanation
exist. It does not establish that the published ciphertext and clues uniquely
determine that construction. An encryption chart with substantial unpublished
information could make independent recovery underdetermined. That is a possibility,
not a conclusion about what Sanborn actually used.

## Is the current approach a dead end?

The ordinary period-27 completion track should be deprioritized. It fits any
ciphertext to the 24 known letters, so its perfect crib match supplies no evidence
for the assumed period. Most resulting plaintext positions are already fixed and
remain incoherent. Phase sweeps merely relabel the same key space.

That does not prove K4 is impossible or eliminate other cipher families. The new
period-26 survivors belong to broader mixed-alphabet affine/progressive models or
feedback models; their compatibility is not a breakthrough. See the
[full report](ASTRA_K4_REPORT_2026-10-07.md) for the precise distinction.

## Priority 1: reconstruct historical inputs before inventing key rules

Obtain dated, public photographs or records of the World Clock's city labels,
time-zone assignments, and ordering as they existed before Kryptos was completed.
Keep uncertain letters or orientations marked as uncertain. Do not silently use
a modern transcription.

This matters for a concrete reason: [Berlin's official visitor information](https://www.berlin.de/en/attractions-and-sights/3561749-3104052-world-clock.en.html)
describes 24 segments, a rotating hour ring, engraved city labels, and a wind-rose
mosaic; it also says city/time-zone assignments were corrected and cities added
after reunification. The current clock can therefore be the wrong research input.
The association between K4 and the World Clock was checked through
[press coverage quoting Sanborn's letter](https://www.aol.com/articles/cia-home-unsolved-puzzle-35-130000201.html),
with the primary-scan retrieval limitation recorded in the full report.

Deliverable before any sweep: a sourced, versioned data table with original
ordering, transcription confidence, and no values chosen from K4's desired plaintext.
Then test a short predeclared list of extraction rules, such as city initials or
time-zone indexing. This is a hypothesis, not evidence that any such rule was used.
The failed simple 24-period progression does not cover label-derived keys.

## Priority 2: test a physically specified two-stage construction

Build an exact coordinate map from the sculpture transcript and independently
verified front/back photographs. Specify the letter permutation and its inverse
before trying plaintext. The transcript displays K4 as a four-letter tail followed
by three full rows; that provides a concrete alternative to inventing an arbitrary
7-by-14 grid. Source: [sculpture transcript](https://www.elonka.com/kryptos/transcript.html).

Test both operation orders for a small, declared family: substitution followed by
the specified permutation, and the permutation followed by substitution. Apply
the cribs at their final plaintext positions. Earlier direct-alignment arithmetic
exclusions do not automatically exclude a transposed intermediate layer.

Deliverable: the positional map, source images or citations, inverse test, exact
parameter count, synthetic recovery controls, and a fixed experiment budget. A
route fitted to the known words after inspecting output is not independent evidence.

## Priority 3: extend the hand-executable cipher families with exact constraints

Use a small documented family of keyed-alphabet tableaux, fractionation, or
stateful switching rules. Encode their actual invariants in a constraint solver,
instead of increasing a keyword list until something looks English. Changing
alphabet order or introducing a transposition must be an explicit parameter;
the old ordinary-ABC exclusions must not be applied outside their scope.

Fit on one crib block and reserve the other for out-of-fit prediction. State the
number of hypotheses examined and include shuffled/random controls; the public
cribs are already known, so this is not a genuinely blind external test. Penalize
or reject constructions whose free parameters can fit arbitrary plaintext.

Deliverable: a falsifiable model with predictions outside the fitted characters,
and a reversible full 97-character implementation. Plausible wording alone is
insufficient. Higher n-gram scores alone cannot authenticate a solution.

## Priority 4: use new authentic information if it becomes public

Publicly released coding-chart excerpts, an authorized clarification, or K5
ciphertext could add constraints that computation cannot manufacture. Any claimed
shared structure between K4 and K5 must be tested against authenticated text, not
an invented reconstruction. These are contingent opportunities, not available
inputs in this repository. No outreach or recurring monitoring has been started.

The next practical action is Priority 1's evidence collection, followed by one
bounded experiment chosen from those independently established inputs. Resume
large searches only when a concrete new constraint or mechanism justifies them.

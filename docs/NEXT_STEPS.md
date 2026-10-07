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

## Completed since the Astra report

The [Opus review](OPUS_K4_REVIEW.md) reproduced Astra's arithmetic and added exact
alphabet-free constraints, earlier-section running-key checks and a registered
keyword-periodic/Gromark experiment. Its arbitrary-alphabet witnesses are distinct
from dictionary-generated alphabets. Its language tests remain heuristic.

The [keyword-progressive experiment](KEYWORD_PROGRESSIVE_REPORT.md) now covers
617,732 keyword alphabets, all cycle drifts, and periods 1–24. Periods 1–23 have no
fit. The six period-24 fits leave 20 plaintext positions unknown, have incoherent
fixed text, and are not an excess over shuffled controls. This does not justify a
completion sweep of their arbitrary remaining key values.

Bean's [HistoCrypt 2021 paper](https://ecp.ep.liu.se/index.php/histocrypt/article/view/153)
is relevant prior work missing from the initial handoff. It motivates direct-alignment
and Gromark hypotheses, not a finding that either is K4's actual mechanism.

## Priority 1: one specifically defined keyword-tableau autokey family

For a future experiment, define a plaintext- or ciphertext-feedback schedule and
its alphabet conventions before running it. Bound primer length and source choices,
and implement its exact inverse. K1/K2 motivate keyword alphabets; they do not
establish that K4 uses autokey. State which equations genuinely predict letters and
which still fit free parameters. The progressive test does not cover autokey.

Deliverable: a fixed design, synthetic recovery and tampering controls, real K1/K2
checks where applicable, exact counts, null comparisons and small reproducible output.
Fit one crib block and test the other where parameters allow it, acknowledging that
both blocks are public. A language score or fitted round trip does not prove a solution.

## Priority 2: calibrate proposed cipher-family statistics

Before a broader key search, compare a small declared set of mechanisms on genuine
English and synthetic controls at length 97. Include the width scan and every
statistic inspected when estimating null behavior. Use likelihood comparisons with
explicit plaintext/key priors. A single extreme statistic does not prove a cipher type.
Opus's width-21 and IC checks illustrate how multiple testing and short text weaken
apparently striking patterns.

## Priority 3: use authentic additional information if it becomes public

Publicly released coding-chart excerpts, an authorized clarification, or K5
ciphertext could add constraints that computation cannot manufacture. Any claimed
shared structure between K4 and K5 must be tested against authenticated text, not
an invented reconstruction. These are contingent opportunities, not available
inputs in this repository. No outreach or recurring monitoring has been started.

Knowing a tableau would fix implied key values at the supplied cribs, strengthening
tests of specified schedules. It would not manufacture repeat checks in a freely
fitted period-27 model. Similar K4/K5 systems do not establish key reuse; matching
BERLINCLOCK ciphertext would support reuse at those eleven positions only.

## Lower-priority open hypotheses

World Clock label keys and physically derived transposition hybrids remain open,
but neither has an independently specified key rule in this repository. Sanborn's
letter, checked through [quoted press coverage](https://www.aol.com/articles/cia-home-unsolved-puzzle-35-130000201.html),
identifies the World Clock in the message's context; it does not disclose a label
extraction rule. Bean also discusses statistical and reported-statement evidence
supporting direct character alignment. Those are reasons to demote these searches,
not mathematical exclusions.

If historical clock inputs become relevant to a concrete hypothesis, obtain dated
transcriptions first. [Berlin's official page](https://www.berlin.de/en/attractions-and-sights/3561749-3104052-world-clock.en.html)
records later city/time-zone changes, so modern lists may be unsuitable. A sculpture
permutation likewise needs a sourced positional map and inverse before scoring.
Resume larger searches only when a concrete new constraint justifies them.

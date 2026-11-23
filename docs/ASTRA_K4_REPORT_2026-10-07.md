# Kryptos K4: Astra audit and fresh bounded attack

Date: 2026-10-07 UTC. **No solution found.** The main result is a correction to the
earlier evidence: period 27 is a convenient way to fit the cribs, not a period
detected in K4. Fresh exact searches exclude several narrowly defined families.
Compatible outputs and full round trips remain distinct from a cryptographic solution.

## Provenance and preservation

- Research run used the requested `gpt-6-astra` model at `xhigh` reasoning effort.
  All reported cipher calculations can be reproduced independently with Python.
- Public repository: [lionatzion/KryptosCipher](https://github.com/lionatzion/KryptosCipher).
  GitHub's branch API and the historical local clone both reported
  `16a05937f4661ed30619dc8fbbd03e29991c1955`, dated 2025-08-26.
- The original checkout and its untracked repository instructions were preserved.
  Research was performed in an isolated clone, then prepared for publication on
  `research/astra-k4-findings-20261007` at the repository owner's request.
- The scripts use the Python standard library. No package installation, model API
  calls from the scripts, accelerator use, or large downloads were required.
- Historical prose references documents and sweeps that are not present as
  executable evidence in the repository. Those claims were not assumed proven.

## Public evidence checked

The [CIA artifact page](https://www.cia.gov/legacy/museum/artifact/kryptos/) still
describes an unresolved fourth section. More recent first-party auction records
distinguish the archive discovery of K4 text from recovery of its cipher method:
[RR Auction, 2025-10-23](https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/).
RR Auction subsequently reported the private archive sale on
[2025-11-21](https://content.rrauction.com/jim-sanborns-complete-kryptos-archive-sells-for-962500-at-auction/).
The auction house explicitly lists both the handwritten K4 plaintext and its
original coding system among the sold materials. In that sense, the archive
contains the answer and method this research is trying to recover independently;
it is more than a single keyword. The sale itself did not publish that method.

[A November 2025 article quoting Sanborn's letter](https://www.aol.com/articles/cia-home-unsolved-puzzle-35-130000201.html)
identifies the relevant Berlin clock as the World Clock and connects the plaintext's
inspiration with Egypt, the Berlin Wall, and message delivery. This is materially
different from a lamp-count clock hypothesis. These are contextual clues, not
numeric key constraints. The original letter's
[DocumentCloud scan](https://www.documentcloud.org/documents/26229389-adobe-scan-nov-12-2025/)
was located but could not be retrieved; the letter details here therefore retain
the qualification that they were checked through quoted press coverage. The
Scientific American and original New York Times pages were also unavailable to
the web tool. No unavailable source was treated as read.

No authenticated public full plaintext plus reproducible mechanism was located
in this source check. A search result claiming a reconstructed plaintext explicitly
acknowledged that its remaining letters were unverified and its parameters fitted;
that text was not used as evidence, a crib, or a training corpus.

The ciphertext was compared with [Elonka Dunin's sculpture transcript](https://www.elonka.com/kryptos/transcript.html),
whose last four ciphertext lines reproduce the repository's K4 exactly:

```text
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

Length: 97. SHA-256, uppercase ASCII with no trailing newline:
`eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab`.
The supplied public anchors give these exact alignments, with 1-based positions:

| Positions | Ciphertext | Plaintext |
|---|---|---|
| 22–25 | FLRV | EAST |
| 26–34 | QQPRNGKSS | NORTHEAST |
| 64–69 | NYPVTT | BERLIN |
| 70–74 | MZFPK | CLOCK |

## What the old scaffold actually proves

For ordinary A=0 Vigenère, `K_i = C_i - P_i (mod 26)`. At period 27, the first
crib block occupies residues `21..26,0..6`; the second occupies `9..19`.
They do not overlap. Consequently:

- There are **24 fitted key parameters and zero independent repeat checks**.
  Every possible ciphertext, including random noise, fits these same 24 plaintext
  observations at period 27. A synthetic control demonstrates this directly.
- The zero-based unknown residues really are `7,8,20`, and there really are
  `26^3 = 17,576` completions. Neither fact supplies positive evidence for this period.
- Zero shifts at positions 33 and 74 follow from the supplied S/S and K/K
  alignments under this particular arithmetic. They add no information and are
  not separate public claims about the encryption mechanism.
- In the ordinary Vigenère track, periods 1–26 and 30–52 conflict with the cribs.
  Periods 27–29 and 53–97 fit. In particular, 28 and 29 are not contradicted by
  the cribs. They also have zero independent repeat checks. This statement is
  restricted to the specified arithmetic and direct alignment.
- Changing the phase while deriving the key constraints with that same phase
  just relabels the key. It cannot improve the search space or act as a transposition.

The baseline was reproduced: 17,576 candidates, best historical fitness
`-47.6380`, key `YYGCKAZABMUYKLGKORNAIBLZCDC`. All completions share 86 fixed
plaintext characters; only 11 positions change:

```text
QDEPKOY??VANRHIBUOOB?EASTNORTHEAST??KZSIYKIENXZ?VPUHHJWFCYMIO??BERLINCLOCK?FSLXURLEXGWKV??OAGARUH
```

The exact crib fit does not rescue the incoherent fixed portions. This is strong
practical reason to deprioritize the model, not a formal proof that English is impossible.

The export audit checked seven existing files. The two older complete CSVs contain
150 phase-zero reproducible rows. The root JSON and root lightweight CSV contain
110 rows requiring phase **26**, which they do not record. The `data/exports`
JSON is a 33-character ellipsis placeholder, not a full plaintext. Six other rows
lack either a plaintext or a key. Historical scores were not independently validated.

`route_transposition.py` returns the identity permutation. The transposition notebook
is a TODO, and several other notebooks are headings only. Thus the repository does
not substantiate the claimed broad transposition, clock, or tableau eliminations.
Those claims were not silently promoted to proven results or repeated as large sweeps.

## Fresh experiments and exact limits

The alphabet systems use `C_num = a*P_num + K (mod 26)`. Plaintext and ciphertext
each use either ordinary ABC or `KRYPTOSABCDEFGHIJLMNQUVWXZ`; `a` ranges over all
12 units modulo 26 unless stated otherwise. There are 48 such systems. This
includes Vigenère (`a=1`) and Beaufort (`a=-1`). Negating the free key covers the
variant Beaufort sign convention without adding an independent search family.
All experiments assume direct character alignment: no transposition, null insertion,
or deletion. Counts below are parameter tuples, not independent statistical trials.

| Experiment | Exhaustive scope | Result |
|---|---|---|
| Affine key recurrence | `K_i = c + sum(b_j*K_(i-j))`, orders 1–8, all coefficients modulo 26, arbitrary initial state, 48 systems | All 384 system/order cases eliminated. 348 fail local equations; 36 order-8 cases require checking 1,872 coefficient vectors against the second crib block. Zero survivors; no cap reached. |
| Progressive repeating key | `K_i=B[(i+h)%m]+d*floor((i+h)/m)`, `m=1..26`, every `h`, every `d=0..25`, arbitrary base key, 48 systems | 438,048 tuples. Every period 1–25 fails, including the proposed 24-sector model. Period 26 has 1,248 compatible tuples, representing 48 families after phase deduplication. |
| Complete period-26 survivors | All `26^3` free-key completions in each of those 48 families | 843,648 full 97-character decryptions ranked; no completion cap or skipped family. Best-ranked outputs remain incoherent. This is not a formal language-based elimination. |
| Plaintext feedback/autokey | `C_i=a*P_i+b*P_(i-L)+t`, `L=1..48`, `a,b=±1`, all 26 `t`, four alphabet pairs, arbitrary L-character primer | 19,968 parameter tuples; 1,298 compatible. Lags 1–25 and 31–48 fail. Survivors: 26 (34), 27 (416), 28 (416), 29 (416), 30 (16). Their primer strings were not exhaustively ranked. |
| Earlier-section running key | Seven streams derived from K1–K3, every cyclic start, both directions, both key alphabets, all 48 systems and all 26 offsets | 11,980,800 tuples, zero 24/24 crib hits. Best partial match is only 8/24 and is not a candidate. |

The recurrence search solves linear equations over GF(2) and GF(13), then uses
the Chinese remainder theorem to enumerate all surviving coefficient vectors.
The first crib block supplies enough consecutive key values to propagate to the
second. A contradiction there rejects every possible original seed, without
guessing unseen plaintext. The enumeration cap is explicit and would leave a
case unresolved; it was never reached.

The clock-motivated progression test is deliberately a specific equation. Its
failure at period 24 does **not** rule out the World Clock, city labels, geographic
ordering, nonlinear wheels, changing alphabets, or a different cryptographic family.
Phase duplicates are removed for completion because their wrap increments can be
absorbed into the free base key.

The feedback test enumerates all 26 starting plaintext values in each residue
chain and checks all observed letters. It establishes exact feasibility, not a
word guess. Compatible primer counts are 17,576 at lags 26/27; 456,976 at 28;
11,881,376 at 29; and 8,031,810,176 at 30. Many surviving cases remain highly
flexible. The JSON contains all surviving parameter tuples, without pretending
they are promising plaintexts.

The seven running-key streams are K1, K2, K3 ciphertext; K1 plaintext; K2 plaintext
as inscribed; concatenated K1–K3 ciphertext; and concatenated K1/K2 plaintext.
Their total lengths sum to 2,400. K1/K2 plaintext was derived from the known
PALIMPSEST/ABSCISSA keys and checked by forward encryption. K2 retains its
as-inscribed `IDBYROWS` ending. The corrected `XLAYERTWO` variant, K3 plaintext,
other books, arbitrary decimations, and noncyclic extraction are outside this search.

The new ranking excludes both crib letters and every n-gram window touching a
crib. It is a simple frequency/bigram heuristic, not a calibrated language model.
The top ten completed progressive outputs include all key parameters and pass
97/97 ciphertext regeneration. Their `is_solution` field remains false. There
is no independent evidence for those fitted keys and no coherent recovered message.

## Why period 26 can survive a broader test

The historical elimination applies to ordinary ABC Vigenere with a strictly
repeating key. Positions 22 and 74, separated by 52 characters, would use the
same period-26 key residue. They instead require key values 1 and 0, so that
particular model is contradicted.

The progressive search permits two different letter alphabets, an affine
plaintext multiplier, and a key increment between successive 26-character cycles.
Its 48 surviving phase-zero families all use different plaintext and ciphertext
alphabets. Forty-six have nonzero drift. Two have zero drift:

| Plaintext alphabet | Ciphertext alphabet | Multiplier a | Drift d |
|---|---|---|---|
| ABC | KRYPTOS | 11 | 0 |
| KRYPTOS | ABC | 9 | 0 |

Those two cases are periodic affine substitutions outside the ordinary Vigenere
model previously rejected. They pass the single repeated-residue comparison;
the other 23 observed residues simply fit free base-key values. The 34 surviving
lag-26 feedback configurations are a different family again: a feedback lag is
not a repeating-key period. None of these compatible models establishes progress
in recovering additional plaintext.

For prioritized future work, see [NEXT_STEPS.md](NEXT_STEPS.md).

## Repairs and validation

Two bugs in `kryptos_k4_p27_sweep_phased.py` were repaired: an indentation error
prevented import, and the CLI omitted the phase when decrypting. Phase and period
are now written to its JSON/CSV exports. Existing historical exports were preserved.
A README notice points to this report instead of presenting the old scaffold as fact.

Thirteen standard-library tests pass. They cover exact input indexing, all 48
affine-system round trips, ciphertext tampering, modular linear algebra including
noninvertible cases, synthetic progressive and recurrence recovery, feedback
positive controls, scoring isolation, phase equivalence, and an end-to-end phased
CLI export. The repaired CLI smoke run finds the expected eight candidates with
`--letters AB`; all repository Python sources parse.

## Reproduce and inspect

From this checkout:

```bash
python3 -m unittest discover -s tests -v
python3 -m research.run_astra
python3 kryptos_k4_p27_sweep.py --outdir out/astra_20261007/baseline --topn 10
python3 kryptos_k4_p27_sweep_phased.py --phase 1 --letters AB --topn 5 --outdir out/astra_20261007/phase_smoke
```

The six new experiment outputs are in [`out/astra_20261007`](../out/astra_20261007):
`audit.json`, `recurrence.json`, `progressive.json`, `feedback.json`, `running.json`,
and `complete.json`. Reproduction needs only Python 3.10+ and no network.
On this Mac, the full new experiment command took about 22 seconds in one process;
the checkout and results together were about 1 MiB before the local commit.
No timing or memory claim is inferred for other machines.

## What remains open

K4's mechanism and 73 unconfirmed plaintext characters remain unknown. The exact
eliminations above apply only to their explicit algebra and indexing. A later
attempt should require an independently motivated key rule or transformation that
makes predictions outside fitted cribs. Appropriate next tests include a verified
1989 World Clock label ordering, or a concrete two-stage mechanism with its inverse
specified before scoring. Such historical inputs have not been collected here;
modern clock city lists must not be silently substituted.

Do not resume period-27 completion ranking or phase sweeps as though they were
new evidence. Do not call the unexecuted historical route/clock/tableau claims
proven eliminations. A credible solution must explain the key, preserve the known
anchors, yield a coherent complete message, and reproduce all 97 ciphertext
characters through an independently justified reversible mechanism. Even those
internal checks alone cannot authenticate a deliberately back-solved construction.

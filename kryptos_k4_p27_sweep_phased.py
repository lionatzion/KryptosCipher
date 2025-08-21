#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kryptos K4 — Period-27 keystream sweep (constraint-driven)
==========================================================

What this does
--------------
- Treats K4 as final-layer: repeating Vigenère-style keystream with period 27.
- Uses the four confirmed plaintext islands as hard constraints:
    EAST at 22–25, NORTHEAST at 26–34, BERLIN at 64–69, CLOCK at 70–74.
- Enforces zero-shift (“A”) at positions 33 and 74 (1-based), per public clues.
- Derives the per-residue keystream constraints from these anchors.
- Enumerates the remaining unknown residues in the 27-cycle (typically 3 of 27).
- Decrypts all 97 chars for each fill, scores the English-likeness, and exports:
    • k4_top10_summary.json
    • k4_top100_candidates_light.csv

Why period 27?
--------------
A 27-beat cycle fits all island-derived shift constraints without conflict and
aligns with the sculpture’s anomalous “extra L” row on the right-panel tableau.
This script lets the constraints themselves decide which residues are unknown,
so it remains robust if you adjust anchors or add new ones later.

Usage
-----
$ python kryptos_k4_p27_sweep.py --outdir ./out --limit 100

Optional flags:
  --period 27            # default; you can also try 28/29 for completeness
  --enforce-a 33 74      # positions (1-based) forced to zero-shift A
  --no-enforce-a         # disable A-enforcement (not recommended)
  --topn 100             # how many rows to keep in CSV (default 100)
  --emit-json            # also write the top-10 JSON (default on)
  --emit-csv             # also write the top-100 CSV (default on)

Outputs land in --outdir (created if missing).

Notes
-----
- “Ciphertext index” in this file is 1-based in comments to match community docs;
  code uses 0-based internally where natural.
- Scoring is light but effective: combines letter-frequency chi-square,
  common bigram counts, and function-word hits (THE, OF, TO, IN, ON, AND, IS, IT, AS, AT).
  You can swap in a heavier n-gram LM later if desired.
- No transposition layer is applied here. Keep this as your baseline and add a
  tiny, reversible route-cipher step elsewhere if it *improves* local function words.

Author: K4 Working Notebook (public-domain helper script)
"""
from __future__ import annotations

import argparse
import csv
import itertools as it
import json
import math
import os
from collections import Counter
from typing import Dict, List, Tuple

ALPH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
A2I = {c:i for i,c in enumerate(ALPH)}
I2A = {i:c for i,c in enumerate(ALPH)}
LETTERS = ALPH

# --- Standard 97-char K4 ciphertext ---
CIPHERTEXT = (
    "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYP"
    "VTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
)

assert len(CIPHERTEXT) == 97, f"Ciphertext length is {len(CIPHERTEXT)}, expected 97."

# --- Confirmed plaintext islands (1-based start, inclusive) ---
ISLANDS = [
    (22, "EAST"),
    (26, "NORTHEAST"),
    (64, "BERLIN"),
    (70, "CLOCK"),
]

# --- Default positions that must have shift 'A' (zero) ---
DEFAULT_ENFORCE_A = [33, 74]  # 1-based


# --------------------------- Helpers ---------------------------
def mod26(x: int) -> int:
    return x % 26

def k_letter_from_CP(c: str, p: str) -> str:
    """Given ciphertext letter c and plaintext letter p, compute keystream letter K s.t. p = c - K (mod 26).
       Rearranged: K = c - p (mod 26)."""
    return I2A[mod26(A2I[c] - A2I[p])]

def decrypt_with_keystream(cipher: str, ks_cycle: List[str], phase: int = 0) -> str:
    out = []
    L = len(ks_cycle)
    for i, c in enumerate(cipher):
        k = ks_cycle[(i + phase) % L]
        p = I2A[mod26(A2I[c] - A2I[k])]
        out.append(p)
    return "".join(out)

def derive_constraints_from_islands(cipher: str, islands: List[Tuple[int, str]], period: int, phase: int = 0) -> Dict[int, str]:
    """Return mapping residue -> keystream letter (A..Z) forced by islands.
       Residue is (pos-1) % period where pos is 1-based index into ciphertext/plaintext."""
    constraints: Dict[int, str] = {}
    for start1b, plain in islands:
        for offset, p_ch in enumerate(plain):
            pos1b = start1b + offset
            c_ch = cipher[pos1b - 1]
            k_ch = k_letter_from_CP(c_ch, p_ch)
            r = (pos1b - 1 + phase) % period
            if r in constraints and constraints[r] != k_ch:
                raise ValueError(f"Constraint conflict at residue {r}: {constraints[r]} vs {k_ch}")
            constraints[r] = k_ch
    return constraints

def enforce_A_positions(constraints: Dict[int, str], enforce_positions_1b: List[int], period: int, phase: int = 0) -> Dict[int, str]:
    out = dict(constraints)
    for pos1b in enforce_positions_1b:
        r = (pos1b - 1 + phase) % period
        k = 'A'
        if r in out and out[r] != k:
            raise ValueError(f"'A' enforcement conflicts at residue {r}: {out[r]} vs 'A'")
        out[r] = k
    return out


# --------------------------- Scoring ---------------------------
# Simple English fitness combining chi-square vs typical letter frequencies,
# common bigrams, and function-word hits.
EN_LETTER_FREQ = {
    # typical percentages (rough), normalized in score function
    'E':12.7,'T':9.1,'A':8.2,'O':7.5,'I':7.0,'N':6.7,'S':6.3,'H':6.1,'R':6.0,
    'D':4.3,'L':4.0,'C':2.8,'U':2.8,'M':2.4,'W':2.4,'F':2.2,'G':2.0,'Y':2.0,
    'P':1.9,'B':1.5,'V':1.0,'K':0.8,'J':0.15,'X':0.15,'Q':0.10,'Z':0.07
}
COMMON_BIGRAMS = ["TH","HE","IN","ER","AN","RE","ON","AT","EN","ND","TI","ES","OR","TE","OF","ED"]
FUNC_WORDS = ["THE","OF","TO","IN","ON","AND","IS","IT","AS","AT"]

def chi_square_score(text: str) -> float:
    """Lower chi-square is better; invert to make higher-is-better."""
    N = len(text)
    counts = Counter(text)
    chi = 0.0
    for ch, pct in EN_LETTER_FREQ.items():
        expected = pct/100.0 * N
        observed = counts.get(ch, 0)
        # classic chi-square component
        if expected > 0:
            chi += (observed - expected)**2 / expected
    # invert and rescale
    return -chi

def bigram_score(text: str) -> float:
    return sum(text.count(bg) for bg in COMMON_BIGRAMS) * 1.0

def func_word_score(text: str) -> float:
    return sum(text.count(w) for w in FUNC_WORDS) * 2.0

def english_fitness(text: str) -> float:
    # Weighted sum; tweakable
    return chi_square_score(text) * 0.5 + bigram_score(text) * 1.0 + func_word_score(text) * 1.5


# --------------------------- Main search ---------------------------
def fill_cycle(constraints: Dict[int, str], period: int, unknown_letters: List[str]) -> List[Tuple[List[str], Dict[int,str]]]:
    """Return list of (cycle, mapping_for_unknowns) for all fills of unconstrained residues with letters from unknown_letters."""
    base = [None]*period
    for r, ch in constraints.items():
        base[r] = ch

    unknown_residues = [r for r in range(period) if base[r] is None]
    results = []

    for fill in it.product(unknown_letters, repeat=len(unknown_residues)):
        ks = base[:]
        mapping = {}
        for r, ch in zip(unknown_residues, fill):
            ks[r] = ch
            mapping[r] = ch
        if any(x is None for x in ks):
            continue
        results.append((ks, mapping))
    return results

def validate_islands(plain: str, islands: List[Tuple[int,str]]) -> bool:
    for start1b, text in islands:
        if plain[start1b-1:start1b-1+len(text)] != text:
            return False
    return True

def main():
    ap = argparse.ArgumentParser(description="Kryptos K4 P=27 keystream sweep with island constraints.")
    ap.add_argument("--period", type=int, default=27, help="Keystream period (default 27).")
    ap.add_argument("--no-enforce-a", action="store_true", help="Disable A-enforcement at DEFAULT_ENFORCE_A.")
    ap.add_argument("--enforce-a", type=int, nargs="*", default=None, help="Override A-enforcement positions (1-based).")
    ap.add_argument("--letters", type=str, default=ALPH, help="Letters to use for unknown residues (default A..Z).")
    ap.add_argument("--topn", type=int, default=100, help="How many rows to keep for CSV output (default 100).")
    ap.add_argument("--outdir", type=str, default=".", help="Output directory.")
ap.add_argument("--phase", type=int, default=0, help="Keystream phase offset (0..period-1).")
    ap.add_argument("--emit-json", action="store_true", default=True, help="Emit top-10 JSON summary (default True).")
    ap.add_argument("--emit-csv", action="store_true", default=True, help="Emit top-100 CSV (default True).")
    args = ap.parse_args()
    phase = getattr(args, "phase", 0)

    period = args.period
    enforce_positions = [] if args.no_enforce_a else (args.enforce_a if args.enforce_a is not None else DEFAULT_ENFORCE_A)

    # 1) Derive constraints from islands
    constraints = derive_constraints_from_islands(CIPHERTEXT, ISLANDS, period, phase=phase)

    # 2) Enforce 'A' at chosen positions
    if enforce_positions:
        constraints = enforce_A_positions(constraints, enforce_positions, period, phase=phase)

    # 3) Prepare all fills of unknown residues
    fills = fill_cycle(constraints, period, list(args.letters))

    # 4) Evaluate all fills
    scored_rows = []
    for ks_cycle, mapping in fills:
        # Build 97-length decryption
        plain = decrypt_with_keystream(CIPHERTEXT, ks_cycle)

        # Hard check: islands must match exactly
        if not validate_islands(plain, ISLANDS):
            continue

        # Score
        score = english_fitness(plain)

        # Pretty strings
        ks_str = "".join(ks_cycle)

        # Track just the residues we actually filled (sorted by residue)
        unknown_residues_sorted = sorted(mapping.keys())
        unknown_str = ", ".join(f"r{r}={mapping[r]}" for r in unknown_residues_sorted)

        scored_rows.append({
            "score": score,
            "keystream_27": ks_str,
            "unknown_fill": unknown_str,
            "plaintext": plain
        })

    # 5) Rank & export
    scored_rows.sort(key=lambda d: d["score"], reverse=True)
    topn = max(1, min(args.topn, len(scored_rows)))

    os.makedirs(args.outdir, exist_ok=True)

    # CSV (light): rank, score, unknown residues (expanded), keystream_27
    if args.emit_csv and scored_rows:
        csv_path = os.path.join(args.outdir, "k4_top100_candidates_light.csv")
        fieldnames = ["rank", "score", "unknown_fill", "keystream_27"]
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for i, row in enumerate(scored_rows[:topn], start=1):
                w.writerow({
                    "rank": i,
                    "score": f"{row['score']:.4f}",
                    "unknown_fill": row["unknown_fill"],
                    "keystream_27": row["keystream_27"],
                })

    # JSON (top-10): full strings including plaintext
    if args.emit_json and scored_rows:
        json_path = os.path.join(args.outdir, "k4_top10_summary.json")
        top10 = []
        for i, row in enumerate(scored_rows[:10], start=1):
            top10.append({
                "rank": i,
                "score": float(f"{row['score']:.4f}"),
                "unknown_fill": row["unknown_fill"],
                "keystream_27": row["keystream_27"],
                "plaintext": row["plaintext"]
            })
        with open(json_path, "w") as f:
            json.dump(top10, f, indent=2)

    # Also write a tiny README for provenance
    readme_path = os.path.join(args.outdir, "README_K4_exports.txt")
    with open(readme_path, "w") as f:
        f.write(
            "Kryptos K4 — Period-27 sweep exports\n"
            "====================================\n\n"
            f"Ciphertext length: {len(CIPHERTEXT)}\n"
            f"Period tested: {period}\n"
            f"A-enforced positions (1-based): {enforce_positions}\n"
            "Anchors: EAST(22–25), NORTHEAST(26–34), BERLIN(64–69), CLOCK(70–74)\n"
            "Files:\n"
            "- k4_top100_candidates_light.csv\n"
            "- k4_top10_summary.json\n"
        )

    # Print quick console summary
    print(f"[done] candidates that satisfy islands: {len(scored_rows)}")
    if scored_rows:
        best = scored_rows[0]
        print(f"[best] score={best['score']:.4f}")
        print(f"[best] keystream_27={best['keystream_27']}")
        print(f"[best] unknown_fill={best['unknown_fill']}")
        print(f"[best] plaintext={best['plaintext']}")

if __name__ == "__main__":
    main()

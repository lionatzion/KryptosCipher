#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kryptos K4 — Period-27 keystream sweep (constraint-driven)
==========================================================

This script is the baseline Vigenère-only solver. It assumes no transposition
has been applied to the ciphertext and searches for a period-27 keystream that
satisfies the known plaintext island constraints.

For searching transposition ciphers, see `transposition_search.py`.
"""
from __future__ import annotations

import argparse
import csv
import json
import os

# --- Local Imports ---
from k4_analysis_lib import (
    CIPHERTEXT,
    ISLANDS,
    DEFAULT_ENFORCE_A,
    analyze_cipher,
    decrypt_with_keystream,
    fill_cycle,
    derive_constraints_from_islands,
    enforce_A_positions,
)
from scoring import english_fitness

def main():
    ap = argparse.ArgumentParser(description="Kryptos K4 P=27 keystream sweep with island constraints.")
    ap.add_argument("--period", type=int, default=27, help="Keystream period (default 27).")
    ap.add_argument("--no-enforce-a", action="store_true", help="Disable A-enforcement at DEFAULT_ENFORCE_A.")
    ap.add_argument("--enforce-a", type=int, nargs="*", default=None, help="Override A-enforcement positions (1-based).")
    ap.add_argument("--letters", type=str, default="ABCDEFGHIJKLMNOPQRSTUVWXYZ", help="Letters to use for unknown residues (default A..Z).")
    ap.add_argument("--topn", type=int, default=100, help="How many rows to keep for CSV output (default 100).")
    ap.add_argument("--outdir", type=str, default=".", help="Output directory.")
    ap.add_argument("--emit-json", action="store_true", default=True, help="Emit top-10 JSON summary (default True).")
    ap.add_argument("--emit-csv", action="store_true", default=True, help="Emit top-100 CSV (default True).")
    args = ap.parse_args()

    period = args.period
    enforce_positions = [] if args.no_enforce_a else (args.enforce_a if args.enforce_a is not None else DEFAULT_ENFORCE_A)

    # 1) Derive constraints from islands
    constraints = derive_constraints_from_islands(CIPHERTEXT, ISLANDS, period)
    if constraints is None:
        print("Error: Island constraints conflict.")
        return

    # 2) Enforce 'A' at chosen positions
    if enforce_positions:
        constraints = enforce_A_positions(constraints, enforce_positions, period)
        if constraints is None:
            print("Error: 'A' enforcement conflicts with island constraints.")
            return

    # 3) Prepare all fills of unknown residues
    # Note: we use a local fill_cycle that includes the mapping for the output
    base = [None]*period
    for r, ch in constraints.items():
        base[r] = ch
    unknown_residues = [r for r in range(period) if base[r] is None]

    fills = []
    import itertools as it
    for fill_letters in it.product(list(args.letters), repeat=len(unknown_residues)):
        ks = base[:]
        mapping = {}
        for r, ch in zip(unknown_residues, fill_letters):
            ks[r] = ch
            mapping[r] = ch
        if any(x is None for x in ks):
            continue
        fills.append((ks, mapping))


    # 4) Evaluate all fills
    scored_rows = []
    for ks_cycle, mapping in fills:
        plain = decrypt_with_keystream(CIPHERTEXT, ks_cycle)
        score = english_fitness(plain)

        unknown_residues_sorted = sorted(mapping.keys())
        unknown_str = ", ".join(f"r{r}={mapping[r]}" for r in unknown_residues_sorted)

        scored_rows.append({
            "score": score,
            "keystream_27": "".join(ks_cycle),
            "unknown_fill": unknown_str,
            "plaintext": plain
        })

    # 5) Rank & export
    scored_rows.sort(key=lambda d: d["score"], reverse=True)
    topn = max(1, min(args.topn, len(scored_rows)))

    os.makedirs(args.outdir, exist_ok=True)

    # CSV
    if args.emit_csv and scored_rows:
        csv_path = os.path.join(args.outdir, f"k4_top{topn}_candidates_p{period}.csv")
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

    # JSON
    if args.emit_json and scored_rows:
        json_path = os.path.join(args.outdir, f"k4_top10_summary_p{period}.json")
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

    # Provenance
    readme_path = os.path.join(args.outdir, "README_K4_exports.txt")
    with open(readme_path, "w") as f:
        f.write(f"Kryptos K4 — P={period} sweep exports\n"
                f"A-enforced: {enforce_positions}\n")

    # Console summary
    print(f"[done] candidates evaluated: {len(scored_rows)}")
    if scored_rows:
        best = scored_rows[0]
        print(f"[best] score={best['score']:.4f}, ks={best['keystream_27']}, fill='{best['unknown_fill']}'")
        print(f"[best] plaintext={best['plaintext']}")

if __name__ == "__main__":
    main()

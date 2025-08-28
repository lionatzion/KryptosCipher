#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kryptos K4 — Transposition Search Framework
===========================================

This script searches for a transposition layer on top of the period-27 Vigenère
decryption. It applies various transposition routes to the K4 ciphertext and
then runs the established P27 analysis on the result to find high-scoring
plaintext candidates.
"""
from __future__ import annotations

import argparse
from typing import List

# --- Local Imports ---
from k4_analysis_lib import CIPHERTEXT, analyze_cipher

# --- Transposition Route Generators ---

def apply_route(text: str, order: List[int]) -> str:
    """Applies a transposition to a text based on an ordering list."""
    if len(order) > len(text):
        order = [i for i in order if i < len(text)]
    if len(order) != len(text):
        raise ValueError(f"Length mismatch: text is {len(text)}, order is {len(order)}")

    out = [''] * len(text)
    for i, old_idx in enumerate(order):
        out[i] = text[old_idx]
    return "".join(out)

def columnar_route(width: int, height: int) -> List[int]:
    """
    Generates a simple columnar transposition order.
    Text is written into a grid (height x width) and read out by columns.
    """
    order = []
    for c in range(width):
        for r in range(height):
            idx = r * width + c
            if idx < (width * height):
                order.append(idx)
    return order

def get_key_order(keyword: str) -> List[int]:
    """Returns the column order from a keyword. E.g., 'ZEBRAS' -> [5, 2, 1, 3, 0, 4]"""
    sorted_chars = sorted(list(set(keyword)))
    key_map = {ch: i for i, ch in enumerate(sorted_chars)}

    # Get numeric value for each character in keyword
    numeric_key = [key_map[ch] for ch in keyword]

    # Get order of columns
    order = []
    for i in range(len(keyword)):
        min_val = float('inf')
        min_idx = -1
        for j in range(len(numeric_key)):
            if numeric_key[j] < min_val:
                min_val = numeric_key[j]
                min_idx = j
        order.append(min_idx)
        numeric_key[min_idx] = float('inf')

    return order

def keyed_columnar_route(width: int, height: int, keyword: str) -> List[int] | None:
    """
    Generates a keyed columnar transposition order.
    Columns are read out in the order specified by the keyword.
    """
    if len(keyword) != width:
        return None # Keyword must match grid width

    key_order = get_key_order(keyword)

    order = []
    for c in key_order: # Iterate through columns in keyword order
        for r in range(height):
            idx = r * width + c
            if idx < (width * height):
                order.append(idx)
    return order

# --- Main Search Logic ---

def get_factors(n):
    """Returns a list of integer factor pairs for n."""
    factors = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            factors.append((i, n//i))
            if i * i != n:
                factors.append((n//i, i))
    return factors

def main():
    """Main function to drive the transposition search."""
    print("K4 Transposition Search Framework")
    print("=================================")

    top_n_results = []
    TOP_N = 10

    # --- Search 1: Simple Columnar ---
    grid_sizes = sorted(list(set(get_factors(97) + get_factors(98))))
    print(f"\n--- Phase 1: Searching {len(grid_sizes)} simple columnar grids ---")
    for width, height in grid_sizes:
        if width == 1 or height == 1: continue
        print(f"  Testing grid {width}x{height}...", end='', flush=True)
        route = columnar_route(width, height)
        if len(route) < 97: continue
        transposed_cipher = apply_route(CIPHERTEXT, route)
        result = analyze_cipher(transposed_cipher)
        if result:
            print(f" best score: {result['score']:.2f}")
            result['transposition_type'] = 'columnar'
            result['params'] = f'{width}x{height}'
            top_n_results.append(result)
        else:
            print(" conflict")

    # --- Search 2: Keyed Columnar ---
    keywords = ["KRYPTOS", "PALIMPSEST", "BERLIN", "CLOCK", "NORTHEAST", "EAST", "SECRET"]
    print(f"\n--- Phase 2: Searching {len(keywords)} keywords for keyed columnar ---")
    for keyword in keywords:
        width = len(keyword)
        # Find a height that works for our 97-char text
        height = (97 + width - 1) // width

        print(f"  Testing keyword '{keyword}' (grid {width}x{height})...", end='', flush=True)
        route = keyed_columnar_route(width, height, keyword)
        if route is None or len(route) < 97:
            print(" invalid params")
            continue

        transposed_cipher = apply_route(CIPHERTEXT, route)
        result = analyze_cipher(transposed_cipher)

        if result:
            print(f" best score: {result['score']:.2f}")
            result['transposition_type'] = 'keyed_columnar'
            result['params'] = f'key={keyword}, grid={width}x{height}'
            top_n_results.append(result)
        else:
            print(" conflict")

    # --- Report Final Results ---
    top_n_results.sort(key=lambda x: x['score'], reverse=True)
    print("\n\n--- Top Results Across All Searches ---")
    if not top_n_results:
        print("No successful transpositions found that satisfy island constraints.")
    else:
        for i, res in enumerate(top_n_results[:TOP_N]):
            print(f"\n#{i+1} - Score: {res['score']:.4f}")
            print(f"  Transposition: {res['transposition_type']} ({res['params']})")
            print(f"  Keystream:     {res['keystream_27']}")
            print(f"  Plaintext:     {res['plaintext']}")

if __name__ == "__main__":
    main()

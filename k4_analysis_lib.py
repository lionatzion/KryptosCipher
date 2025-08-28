#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kryptos K4 — Analysis Library
=============================

Shared functions for analyzing Kryptos K4 ciphertext, used by both the
period-27 baseline sweep and the transposition search scripts.
"""
from __future__ import annotations

import itertools as it
from typing import Dict, List, Tuple

from scoring import english_fitness

# --- Core Constants ---
ALPH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
A2I = {c: i for i, c in enumerate(ALPH)}
I2A = {i: c for i, c in enumerate(ALPH)}

CIPHERTEXT = (
    "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYP"
    "VTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
)

ISLANDS = [
    (22, "EAST"),
    (26, "NORTHEAST"),
    (64, "BERLIN"),
    (70, "CLOCK"),
]

DEFAULT_ENFORCE_A = [33, 74]

# --- Core Analysis Functions ---

def mod26(x: int) -> int:
    return x % 26

def decrypt_with_keystream(cipher: str, ks_cycle: List[str]) -> str:
    """Decrypts a ciphertext using a repeating Vigenère keystream."""
    out = []
    L = len(ks_cycle)
    for i, c in enumerate(cipher):
        k = ks_cycle[i % L]
        p = I2A[mod26(A2I[c] - A2I[k])]
        out.append(p)
    return "".join(out)

def k_letter_from_CP(c: str, p: str) -> str:
    """Computes keystream letter K given ciphertext C and plaintext P."""
    return I2A[mod26(A2I[c] - A2I[p])]

def derive_constraints_from_islands(cipher: str, islands: List[Tuple[int, str]], period: int) -> Dict[int, str] | None:
    """
    Derives keystream residue constraints from known plaintext islands.
    Returns the constraint map or None if a conflict is found.
    """
    constraints: Dict[int, str] = {}
    for start1b, plain in islands:
        for offset, p_ch in enumerate(plain):
            pos1b = start1b + offset
            c_ch = cipher[pos1b - 1]
            k_ch = k_letter_from_CP(c_ch, p_ch)
            r = (pos1b - 1) % period
            if r in constraints and constraints[r] != k_ch:
                return None  # Conflict
            constraints[r] = k_ch
    return constraints

def enforce_A_positions(constraints: Dict[int, str], enforce_positions_1b: List[int], period: int) -> Dict[int, str] | None:
    """
    Adds 'A' (zero-shift) constraints at specified positions.
    Returns the updated constraint map or None if a conflict is found.
    """
    out = dict(constraints)
    for pos1b in enforce_positions_1b:
        r = (pos1b - 1) % period
        k = 'A'
        if r in out and out[r] != k:
            return None  # Conflict
        out[r] = k
    return out

def fill_cycle(constraints: Dict[int, str], period: int) -> List[List[str]]:
    """
    Generates all possible full keystream cycles by filling in unknown residues
    with all letters from A-Z.
    """
    base = [None] * period
    for r, ch in constraints.items():
        base[r] = ch
    unknown_residues = [r for r in range(period) if base[r] is None]
    results = []
    for fill in it.product(ALPH, repeat=len(unknown_residues)):
        ks = base[:]
        for r, ch in zip(unknown_residues, fill):
            ks[r] = ch
        if any(x is None for x in ks):
            continue
        results.append(ks)
    return results

def analyze_cipher(cipher_text: str, period: int = 27) -> Dict | None:
    """
    Runs the full P27 Vigenère analysis on a given ciphertext.
    This is the main analysis engine, refactored for generic use.
    Returns the best-scoring result found, or None if constraints conflict.
    """
    # 1. Derive constraints from islands and 'A' positions.
    constraints = derive_constraints_from_islands(cipher_text, ISLANDS, period)
    if constraints is None:
        return None

    constraints = enforce_A_positions(constraints, DEFAULT_ENFORCE_A, period)
    if constraints is None:
        return None

    # 2. Fill unknown keystream residues and find the best plaintext.
    best_score = -9999
    best_result = None

    fills = fill_cycle(constraints, period)
    for ks_cycle in fills:
        plain = decrypt_with_keystream(cipher_text, ks_cycle)
        score = english_fitness(plain)

        if score > best_score:
            best_score = score
            best_result = {
                "score": score,
                "keystream_27": "".join(ks_cycle),
                "plaintext": plain
            }

    return best_result

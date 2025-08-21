#!/usr/bin/env python3
from __future__ import annotations
import argparse, os, csv, json, itertools as it
from collections import Counter
from typing import Dict, List, Tuple

ALPH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
A2I = {c:i for i,c in enumerate(ALPH)}
I2A = {i:c for i,c in enumerate(ALPH)}

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

DEFAULT_ENFORCE_A = [33, 74]  # 1-based

# --- scoring ---
EN_LETTER_FREQ = {
    'E':12.7,'T':9.1,'A':8.2,'O':7.5,'I':7.0,'N':6.7,'S':6.3,'H':6.1,'R':6.0,
    'D':4.3,'L':4.0,'C':2.8,'U':2.8,'M':2.4,'W':2.4,'F':2.2,'G':2.0,'Y':2.0,
    'P':1.9,'B':1.5,'V':1.0,'K':0.8,'J':0.15,'X':0.15,'Q':0.10,'Z':0.07
}
COMMON_BIGRAMS = ["TH","HE","IN","ER","AN","RE","ON","AT","EN","ND","TI","ES","OR","TE","OF","ED"]
FUNC_WORDS = ["THE","OF","TO","IN","ON","AND","IS","IT","AS","AT"]

def mod26(x:int)->int: return x%26
def k_from_CP(c:str,p:str)->str: return I2A[(A2I[c]-A2I[p])%26]

def chi_square_score(text: str) -> float:
    N = len(text)
    counts = Counter(text)
    chi = 0.0
    for ch, pct in EN_LETTER_FREQ.items():
        expected = pct/100.0 * N
        observed = counts.get(ch, 0)
        if expected > 0:
            chi += (observed - expected)**2 / expected
    return -chi

def bigram_score(text: str) -> float:
    return sum(text.count(bg) for bg in COMMON_BIGRAMS) * 1.0

def func_word_score(text: str) -> float:
    return sum(text.count(w) for w in FUNC_WORDS) * 2.0

def english_fitness(text: str) -> float:
    return chi_square_score(text)*0.5 + bigram_score(text)*1.0 + func_word_score(text)*1.5

def decrypt(cipher: str, ks_cycle: List[str], phase:int, period:int) -> str:
    out = []
    L = len(ks_cycle)
    for i, c in enumerate(cipher):
        k = ks_cycle[(i + phase) % L]
        p = I2A[(A2I[c]-A2I[k])%26]
        out.append(p)
    return "".join(out)

def derive_constraints(cipher: str, islands: List[Tuple[int,str]], period:int, phase:int)->Dict[int,str]:
    constraints: Dict[int,str] = {}
    for start1b, plain in islands:
        for off, pch in enumerate(plain):
            pos1b = start1b + off
            c = cipher[pos1b-1]
            k = k_from_CP(c, pch)
            r = (pos1b - 1 + phase) % period
            if r in constraints and constraints[r] != k:
                raise ValueError(f"Constraint conflict at residue {r}: {constraints[r]} vs {k}")
            constraints[r] = k
    return constraints

def enforce_A(constraints: Dict[int,str], enforce_positions_1b: List[int], period:int, phase:int)->Dict[int,str]:
    out = dict(constraints)
    for pos1b in enforce_positions_1b:
        r = (pos1b - 1 + phase) % period
        k = 'A'
        if r in out and out[r] != k:
            raise ValueError(f"A-enforcement conflict at residue {r}: {out[r]} vs 'A'")
        out[r] = k
    return out

def fill_cycles(constraints: Dict[int,str], period:int, alphabet:str):
    base = [None]*period
    for r,ch in constraints.items():
        base[r] = ch
    unknown = [r for r in range(period) if base[r] is None]
    for fill in it.product(alphabet, repeat=len(unknown)):
        ks = base[:]
        mapping = {}
        for r,ch in zip(unknown, fill):
            ks[r] = ch
            mapping[r] = ch
        if any(x is None for x in ks):
            continue
        yield ks, mapping, unknown

def validate_islands(plain: str, islands: List[Tuple[int,str]])->bool:
    for start1b, text in islands:
        if plain[start1b-1:start1b-1+len(text)] != text:
            return False
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, default=27)
    ap.add_argument("--phase", type=int, default=0)
    ap.add_argument("--letters", type=str, default=ALPH)
    ap.add_argument("--topn", type=int, default=100)
    ap.add_argument("--outdir", type=str, default=".")
    ap.add_argument("--emit-json", action="store_true", default=True)
    ap.add_argument("--emit-csv", action="store_true", default=True)
    args = ap.parse_args()

    period = args.period
    phase = args.phase
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    constraints = derive_constraints(CIPHERTEXT, ISLANDS, period, phase)
    constraints = enforce_A(constraints, DEFAULT_ENFORCE_A, period, phase)

    rows = []
    for ks, mapping, unknown in fill_cycles(constraints, period, args.letters):
        plain = decrypt(CIPHERTEXT, ks, phase=phase, period=period)
        if not validate_islands(plain, ISLANDS):
            continue
        score = english_fitness(plain)
        rows.append({
            "score": score,
            "keystream_27": "".join(ks),
            "plaintext": plain,
            "unknown_residues": ",".join(map(str, unknown)),
        })

    rows.sort(key=lambda r: r["score"], reverse=True)
    topn = rows[:args.topn]

    if args.emit_csv:
        csv_path = os.path.join(outdir, "k4_top100_candidates_light.csv")
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["score","keystream_27","plaintext","unknown_residues"])
            w.writeheader()
            for r in topn:
                w.writerow(r)

    if args.emit_json:
        json_path = os.path.join(outdir, "k4_top10_summary.json")
        with open(json_path, "w") as f:
            json.dump(topn[:10], f, indent=2)

    print(f"Done: {len(rows)} candidates; wrote outputs to {outdir}")

if __name__ == "__main__":
    main()

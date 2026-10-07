"""Pre-registered keyword-tableau experiment; see docs/OPUS_K4_EXPERIMENT_PREREG.md.

Direct-alignment substitution c(C_i) = p(P_i) + k_i (or Beaufort forms) where p and c
come from dictionary keyword alphabets, ABC, or KRYPTOS, and k follows either a
periodic schedule (S1) or a Gromark-style lagged Fibonacci schedule (S2). Block 1
(EASTNORTHEAST) fits the schedule; block 2 (BERLINCLOCK) is predicted.
"""
from __future__ import annotations

from collections import Counter
from math import log
from pathlib import Path
import random

import numpy as np

from research.opus_review.core import ABC, CRIBS, CRIB_POSITIONS, K4, KA, keyword_alphabet

DICTIONARY = Path("/usr/share/dict/web2")
MODES = ("kryptos", "continue", "columnar")
CONFIGS = ("W/W", "W/ABC", "ABC/W", "W/KA", "KA/W")
PERIODIC_SIGNS = ("vigenere", "beaufort")
NUMERIC_SIGNS = ("vigenere", "variant", "beaufort")
# Fixed before any K4 run (pre-registration): sculpture, site, people and theme words.
CONTEXT_WORDS = (
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "BERLINCLOCK", "WORLDCLOCK",
    "WELTZEITUHR", "URANIA", "ALEXANDERPLATZ", "MENGENLEHREUHR", "EAST", "NORTHEAST",
    "EASTNORTHEAST", "NORTH", "COMPASS", "COMPASSROSE", "LODESTONE", "MAGNETIC", "SANBORN",
    "JIMSANBORN", "JAMESSANBORN", "SCHEIDT", "EDSCHEIDT", "LANGLEY", "CIA", "WEBSTER",
    "WILLIAMWEBSTER", "EGYPT", "CAIRO", "CARTER", "HOWARDCARTER", "TUTANKHAMUN", "TUTANKHAMEN",
    "PHARAOH", "PYRAMID", "SHADOW", "SHADOWFORCES", "ILLUSION", "IQLUSION", "LUCID",
    "LUCIDMEMORY", "VIRTUALLY", "INVISIBLE", "DIGETAL", "INTERPRETATIU", "POSITION",
    "TISYOURPOSITION", "LAYERTWO", "XLAYERTWO", "IDBYROWS", "UNDERGRUUND", "DESPARATLY",
    "MASK", "MASKING", "MATRIX", "SECRET", "MESSAGE", "DELIVERINGAMESSAGE", "BERLINWALL",
    "WALL", "SCULPTURE", "COPPER", "PETRIFIEDWOOD", "ANTIPODES", "HIRSHHORN", "YAR",
    "DYAHR", "ENIGMA", "VIGENERE", "QUAGMIRE", "GROMARK", "SMITHSONIAN", "VIRGINIA",
)


# ------------------------------------------------------------------ alphabet family
def alphabet_family(words=None):
    """Unique keyword alphabets with the first (word, mode) that produced each."""
    if words is None:
        words = [w.strip() for w in DICTIONARY.read_text().splitlines() if w.strip()]
        words += list(CONTEXT_WORDS)
    first = {}
    for word in words:
        for mode in MODES:
            first.setdefault(keyword_alphabet(word, mode), (word, mode))
    alphabets = list(first)
    return alphabets, [first[a] for a in alphabets]


def context_rows(family):
    """Rows of every context-word alphabet, whichever word first produced it."""
    row = {a: n for n, a in enumerate(family[0])}
    return sorted({row[keyword_alphabet(w, m)] for w in CONTEXT_WORDS for m in MODES})


def positions_matrix(alphabets):
    """pos[n, letter] = index of letter in alphabet n."""
    order = np.array([[ord(ch) - 65 for ch in a] for a in alphabets], dtype=np.int16)
    pos = np.empty_like(order)
    pos[np.arange(len(alphabets))[:, None], order] = np.arange(26, dtype=np.int16)
    return pos


def crib_letters(cipher, cribs, positions):
    plain = np.array([ord(cribs[i]) - 65 for i in positions])
    ctext = np.array([ord(cipher[i]) - 65 for i in positions])
    return plain, ctext


def side(pos, letters_, kind):
    """Alphabet indices of the given letters for one side of the tableau."""
    if kind == "W":
        return pos[:, letters_]
    alphabet = ABC if kind == "ABC" else KA
    return np.array([[alphabet.index(chr(65 + x)) for x in letters_]], dtype=np.int16)


def differences(pos, config, sign, cipher=K4, cribs=CRIBS, positions=CRIB_POSITIONS, pos_c=None):
    """Implied key values d (N x 24) for one configuration and sign convention."""
    plain, ctext = crib_letters(cipher, cribs, positions)
    pk, ck = config.split("/")
    p = side(pos, plain, pk)
    c = side(pos if pos_c is None else pos_c, ctext, ck)
    if sign == "vigenere":
        d = c - p
    elif sign == "variant":
        d = p - c
    else:
        d = c + p
    return np.mod(d, 26).astype(np.int16)


# ----------------------------------------------------------------- S1: periodic
def periodic_cells(positions=CRIB_POSITIONS, block1=13, max_period=26):
    """Spanning repeat pairs per period, plus fit/predict bookkeeping."""
    cells = {}
    for p in range(1, max_period + 1):
        first, pairs = {}, []
        for col, i in enumerate(positions):
            r = i % p
            if r in first:
                pairs.append((col, first[r]))
            else:
                first[r] = col
        fitted = {positions[c] % p for c in range(block1)}
        cells[p] = {"pairs": pairs, "checks": len(pairs),
                    "block1_internal_checks": block1 - len(fitted),
                    "block2_predicted": sum(positions[c] % p in fitted for c in range(block1, len(positions)))}
    return cells


def periodic_survivors(d, cells):
    out = {}
    for p, cell in cells.items():
        idx = np.arange(len(d))
        for a, b in cell["pairs"]:
            idx = idx[d[idx, a] == d[idx, b]]
            if not len(idx):
                break
        out[p] = idx
    return out


# ------------------------------------------------------- S2: lagged Fibonacci keys
def gromark_survivors(d, bases=range(2, 27), lags=range(2, 13), offsets=range(26)):
    """Rows whose block-1 key values generate block 2 exactly; returns (row, s, b, L)."""
    hits = []
    for s in offsets:
        v = (d + s) % 26
        vmax = v[:, :13].max(axis=1)
        for base in bases:
            cand = np.flatnonzero(vmax < base)
            if not len(cand):
                continue
            vc = v[cand]
            cols = [np.ascontiguousarray(vc[:, j]) for j in range(24)]
            for lag in lags:
                keep = np.flatnonzero(cols[lag] == (cols[0] + cols[1]) % base)
                for col in range(lag + 1, 13):
                    if not len(keep):
                        break
                    keep = keep[cols[col][keep] == (cols[col - lag][keep] + cols[col - lag + 1][keep]) % base]
                if not len(keep):
                    continue
                seq = {21 + j: cols[j][keep] for j in range(13)}
                for t in range(34, 74):
                    seq[t] = (seq[t - lag] + seq[t - lag + 1]) % base
                good = np.ones(len(keep), bool)
                for j, t in enumerate(range(63, 74)):
                    good &= seq[t] == cols[13 + j][keep]
                hits.extend((int(cand[n]), s, base, lag) for n in keep[good])
    return hits


def gromark_full_key(values_at_block1, base, lag):
    """Extend 13 consecutive key values at 21..33 forwards and backwards to 0..96."""
    key = {21 + j: v for j, v in enumerate(values_at_block1)}
    for t in range(34, 97):
        key[t] = (key[t - lag] + key[t - lag + 1]) % base
    for t in range(20, -1, -1):
        key[t] = (key[t + lag] - key[t + 1]) % base
    return [key[t] for t in range(97)]


# ---------------------------------------------------------------- decryption
def tableau(config, alphabet):
    pk, ck = config.split("/")
    pick = {"W": alphabet, "ABC": ABC, "KA": KA}
    return pick[pk], pick[ck]


def decrypt(cipher, shifts, pa, ca, sign):
    """Invert c(C)=p(P)+k, p(P)-c(C)=k or c(C)+p(P)=k; None shifts give '?'."""
    out = []
    for c, k in zip(cipher, shifts):
        if k is None:
            out.append("?")
            continue
        ci = ca.index(c)
        pi = {"vigenere": ci - k, "variant": ci + k, "beaufort": k - ci}[sign] % 26
        out.append(pa[pi])
    return "".join(out)


def encrypt(plain, shifts, pa, ca, sign):
    out = []
    for p, k in zip(plain, shifts):
        pi = pa.index(p)
        ci = {"vigenere": pi + k, "variant": pi - k, "beaufort": k - pi}[sign] % 26
        out.append(ca[ci])
    return "".join(out)


# ------------------------------------------------------------------ English score
def bigram_model(words):
    counts, total = Counter(), Counter()
    for w in words:
        w = "".join(ch for ch in w.upper() if ch in ABC)
        for a, b in zip(w, w[1:]):
            counts[a + b] += 1
            total[a] += 1
    return {a + b: log((counts[a + b] + 1) / (total[a] + 26)) for a in ABC for b in ABC}


def english_score(text, model, exclude=CRIBS):
    """Mean bigram log-probability over adjacent determined non-crib letters."""
    vals = [model[text[i:i + 2]] for i in range(len(text) - 1)
            if "?" not in text[i:i + 2] and i not in exclude and i + 1 not in exclude]
    return sum(vals) / len(vals) if vals else None


# ------------------------------------------------------------------ one full run
def run_family(cipher=K4, cribs=CRIBS, positions=CRIB_POSITIONS, family=None, pos=None,
               configs=CONFIGS, s2=True, context_pairs=True, keep=2000):
    """All S1 and S2 survivors for one ciphertext, with per-cell counts.

    Survivor details are kept for at most ``keep`` rows per configuration, sign and
    period; counts are always exact and ``truncated`` lists every cap that bound.
    """
    alphabets, sources = family
    cells = periodic_cells(positions)
    s1_counts, s1_hits, s2_hits, tests, truncated = Counter(), [], [], Counter(), []
    for config in configs:
        for sign in PERIODIC_SIGNS:
            d = differences(pos, config, sign, cipher, cribs, positions)
            tests["s1"] += len(d)
            for p, idx in periodic_survivors(d, cells).items():
                s1_counts[p] += len(idx)
                if len(idx) > keep:
                    truncated.append({"config": config, "sign": sign, "period": p, "survivors": int(len(idx))})
                s1_hits.extend({"row": int(n), "config": config, "sign": sign, "period": p,
                                "d": d[n].tolist()} for n in idx[:keep])
        if s2:
            for sign in NUMERIC_SIGNS:
                d = differences(pos, config, sign, cipher, cribs, positions)
                tests["s2_rows"] += len(d)
                s2_hits.extend({"row": r, "config": config, "sign": sign, "offset": s, "base": b,
                                "lag": L, "d": d[r].tolist()} for r, s, b, L in gromark_survivors(d))
    pairs = None
    if context_pairs:
        ctx = context_rows(family)
        left = np.repeat(ctx, len(ctx))
        right = np.tile(ctx, len(ctx))
        distinct = left != right
        left, right = left[distinct], right[distinct]
        pairs = (left, right)
        for sign in PERIODIC_SIGNS:
            d = differences(pos[left], "W/W", sign, cipher, cribs, positions, pos_c=pos[right])
            tests["s1"] += len(d)
            for p, idx in periodic_survivors(d, cells).items():
                s1_counts[p] += len(idx)
                if len(idx) > keep:
                    truncated.append({"config": "W1/W2", "sign": sign, "period": p, "survivors": int(len(idx))})
                s1_hits.extend({"row": int(left[n]), "cipher_row": int(right[n]), "config": "W1/W2",
                                "sign": sign, "period": p, "d": d[n].tolist()} for n in idx[:keep])
        if s2:
            for sign in NUMERIC_SIGNS:
                d = differences(pos[left], "W/W", sign, cipher, cribs, positions, pos_c=pos[right])
                tests["s2_rows"] += len(d)
                s2_hits.extend({"row": int(left[r]), "cipher_row": int(right[r]), "config": "W1/W2",
                                "sign": sign, "offset": s, "base": b, "lag": L, "d": d[r].tolist()}
                               for r, s, b, L in gromark_survivors(d))
    return {"cells": cells, "s1_counts": dict(s1_counts), "s1_hits": s1_hits, "s2_hits": s2_hits,
            "tests": dict(tests), "pairs": pairs, "truncated": truncated}


def expected_false(cells, s1_tests, s2_rows):
    """Analytic false-survivor expectations if implied keys were uniform and independent."""
    s1 = {p: s1_tests * 26.0 ** -c["checks"] for p, c in cells.items()}
    s2 = s2_rows * 26 * sum(b ** L for b in range(2, 27) for L in range(2, 13)) * 26.0 ** -24
    return s1, s2


def describe_s1(hit, cipher, cribs, positions, family):
    alphabets, sources = family
    alphabet = alphabets[hit["row"]]
    if hit["config"] == "W1/W2":
        pa, ca = alphabet, alphabets[hit["cipher_row"]]
    else:
        pa, ca = tableau(hit["config"], alphabet)
    p = hit["period"]
    residue_key = {}
    for col, i in enumerate(positions):
        residue_key.setdefault(i % p, hit["d"][col])
    shifts = [residue_key.get(i % p) for i in range(len(cipher))]
    plain = decrypt(cipher, shifts, pa, ca, hit["sign"])
    assert all(plain[i] == cribs[i] for i in positions)
    return {**{k: v for k, v in hit.items() if k != "d"}, "source": sources[hit["row"]],
            "plain_alphabet": pa, "cipher_alphabet": ca,
            "residue_key": {r: residue_key.get(r) for r in range(p)},
            "decryption": plain, "determined_letters": len(cipher) - plain.count("?")}


def describe_s2(hit, cipher, cribs, family):
    alphabets, sources = family
    alphabet = alphabets[hit["row"]]
    if hit["config"] == "W1/W2":
        pa, ca = alphabet, alphabets[hit["cipher_row"]]
    else:
        pa, ca = tableau(hit["config"], alphabet)
    v = [(x + hit["offset"]) % 26 for x in hit["d"][:13]]
    key = gromark_full_key(v, hit["base"], hit["lag"])
    shifts = [(k - hit["offset"]) % 26 for k in key]
    plain = decrypt(cipher, shifts, pa, ca, hit["sign"])
    assert all(plain[i] == cribs[i] for i in cribs)
    assert encrypt(plain, shifts, pa, ca, hit["sign"]) == cipher
    return {**{k: v for k, v in hit.items() if k != "d"}, "source": sources[hit["row"]],
            "plain_alphabet": pa, "cipher_alphabet": ca, "primer": key[:hit["lag"]],
            "decryption": plain}


# ----------------------------------------------------------------- controls
def planted_s1(family, pos, rng, plain_pool, period):
    alphabets, _ = family
    row = rng.randrange(len(alphabets))
    config, sign = rng.choice(CONFIGS), rng.choice(PERIODIC_SIGNS)
    pa, ca = tableau(config, alphabets[row])
    start = rng.randrange(len(plain_pool) - 97)
    plain = list(plain_pool[start:start + 97])
    for i, ch in CRIBS.items():
        plain[i] = ch
    key = [rng.randrange(26) for _ in range(period)]
    cipher = encrypt("".join(plain), [key[i % period] for i in range(97)], pa, ca, sign)
    d = differences(pos, config, sign, cipher)
    found = periodic_survivors(d, {period: periodic_cells()[period]})[period]
    same = {int(n) for n in found if alphabets[n] == alphabets[row]}
    return {"row": row, "config": config, "sign": sign, "period": period,
            "recovered": row in same, "other_survivors": int(len(found) - len(same))}


def planted_s2(family, pos, rng, plain_pool):
    alphabets, _ = family
    row = rng.randrange(len(alphabets))
    config, sign = rng.choice(CONFIGS), rng.choice(NUMERIC_SIGNS)
    pa, ca = tableau(config, alphabets[row])
    base, lag, offset = rng.randrange(2, 27), rng.randrange(2, 13), rng.randrange(26)
    primer = [rng.randrange(base) for _ in range(lag)]
    key = primer[:]
    while len(key) < 97:
        key.append((key[-lag] + key[-lag + 1]) % base)
    start = rng.randrange(len(plain_pool) - 97)
    plain = list(plain_pool[start:start + 97])
    for i, ch in CRIBS.items():
        plain[i] = ch
    cipher = encrypt("".join(plain), [(k - offset) % 26 for k in key], pa, ca, sign)
    d = differences(pos, config, sign, cipher)
    hits = gromark_survivors(d)
    return {"row": row, "config": config, "sign": sign, "base": base, "lag": lag, "offset": offset,
            "recovered": any(r == row and s == offset and b == base and L == lag for r, s, b, L in hits),
            "other_survivors": sum(r != row for r, s, b, L in hits)}


def experiment(seed=20261007, s1_nulls=40, s2_nulls=10, planted_s1_runs=30, planted_s2_runs=20, log=print):
    """Controls first, then K4, then shuffled-ciphertext nulls (pre-registered order)."""
    import hashlib
    import time
    from research.opus_review.audit import sculpture_texts
    from research.opus_review.core import ROOT
    started = time.time()
    prereg = ROOT / "docs/OPUS_K4_EXPERIMENT_PREREG.md"
    family = alphabet_family()
    pos = positions_matrix(family[0])
    deviations = [
        "2026-10-07 05:36Z: the first K4 run crashed inside run_family (a local variable shadowed "
        "the 'keep' cap) before writing or printing any K4 result. Renamed the variable and reran. "
        "No family, control, or acceptance rule changed.",
    ]
    out = {"prereg_sha256": hashlib.sha256(prereg.read_bytes()).hexdigest(), "deviations": deviations,
           "family": {"alphabets": len(family[0]), "dictionary": str(DICTIONARY),
                      "dictionary_lines": sum(1 for w in DICTIONARY.read_text().splitlines() if w.strip()),
                      "context_words": len(CONTEXT_WORDS), "context_alphabets": len(context_rows(family)),
                      "modes": MODES, "configs": CONFIGS + ("W1/W2 context pairs",)}}
    log("real positive controls")
    out["real_positive_controls"] = real_positive_controls(family, pos)
    rng = random.Random(seed)
    pool = sculpture_texts()[2]["K1K2K3_plain_corrected"]
    log("planted controls")
    open_periods = (8, 13, 16, 19, 20, 23, 24)
    s1 = [planted_s1(family, pos, rng, pool, rng.choice(open_periods) if n % 2 == 0 else rng.randrange(1, 27))
          for n in range(planted_s1_runs)]
    s2 = [planted_s2(family, pos, rng, pool) for _ in range(planted_s2_runs)]
    out["planted_controls"] = {"s1_recovered": sum(r["recovered"] for r in s1), "s1_runs": len(s1),
                               "s2_recovered": sum(r["recovered"] for r in s2), "s2_runs": len(s2),
                               "s1": s1, "s2": s2}
    log("K4 run")
    k4 = run_family(family=family, pos=pos)
    cells = k4["cells"]
    exp_s1, exp_s2 = expected_false(cells, k4["tests"]["s1"], k4["tests"]["s2_rows"])
    reportable = {p for p, e in exp_s1.items() if e < 0.05}
    model = bigram_model(DICTIONARY.read_text().split())
    described = [describe_s1(h, K4, CRIBS, CRIB_POSITIONS, family) for h in k4["s1_hits"] if h["period"] in reportable]
    for h in described:
        h["english_score"] = english_score(h["decryption"], model)
    weak = [h for h in k4["s1_hits"] if h["period"] not in reportable]
    null_scores = sorted(s for s in (english_score(describe_s1(h, K4, CRIBS, CRIB_POSITIONS, family)["decryption"], model)
                                     for h in random.Random(seed).sample(weak, min(2000, len(weak)))) if s is not None)
    s2_described = [describe_s2(h, K4, CRIBS, family) for h in k4["s2_hits"]]
    for h in s2_described:
        h["english_score"] = english_score(h["decryption"], model)
    out["k4"] = {
        "tests": k4["tests"],
        "detail_caps_that_bound": k4["truncated"],
        "caps_bound_in_reportable_cells": [t for t in k4["truncated"] if t["period"] in reportable],
        "s1_cells": {p: {"checks": c["checks"], "block1_internal_checks": c["block1_internal_checks"],
                         "block2_predicted_letters": c["block2_predicted"], "expected_false": exp_s1[p],
                         "reportable": p in reportable, "survivors": k4["s1_counts"].get(p, 0)}
                     for p, c in cells.items()},
        "s1_reportable_survivors": described,
        "s1_weak_cell_examples": [describe_s1(h, K4, CRIBS, CRIB_POSITIONS, family) for h in weak[:5]],
        "s2_expected_false_total": exp_s2, "s2_survivors": s2_described,
        "null_english_score_from_weak_cells": {"n": len(null_scores),
                                               "p99": null_scores[int(0.99 * len(null_scores))] if null_scores else None,
                                               "max": null_scores[-1] if null_scores else None},
    }
    log("shuffled-ciphertext nulls")
    nulls = []
    for n in range(max(s1_nulls, s2_nulls)):
        shuffled = "".join(random.Random(seed + 1000 + n).sample(K4, 97))
        res = run_family(cipher=shuffled, family=family, pos=pos, s2=n < s2_nulls)
        nulls.append({"seed": seed + 1000 + n, "s1_counts": res["s1_counts"],
                      "s2_survivors": len(res["s2_hits"]) if n < s2_nulls else None})
    agg = {p: sum(r["s1_counts"].get(p, 0) for r in nulls) / len(nulls) for p in cells}
    out["nulls"] = {"s1_runs": len(nulls), "s2_runs": s2_nulls, "s1_mean_survivors": agg,
                    "s1_runs_with_any_reportable_survivor": sum(any(r["s1_counts"].get(p, 0) for p in reportable) for r in nulls),
                    "s2_total_survivors": sum(r["s2_survivors"] or 0 for r in nulls), "runs": nulls}
    out["seconds"] = round(time.time() - started, 1)
    return out


def real_positive_controls(family, pos):
    """Sanborn's own K1 and K2 must be recovered by the S1 machinery."""
    from research.opus_review.audit import sculpture_texts
    texts = sculpture_texts()[0]
    ka_row = family[0].index(KA)
    out = []
    k2c, k2p = texts["K2_cipher"], texts["K2_plain_as_inscribed"]
    for start in (0, 60, 120, 180, 240):
        cipher = k2c[start:start + 97]
        cribs = {i: k2p[start + i] for i in CRIB_POSITIONS}
        cells = periodic_cells(CRIB_POSITIONS)
        d = differences(pos, "W/W", "vigenere", cipher, cribs, CRIB_POSITIONS)
        surv = periodic_survivors(d, cells)
        out.append({"control": f"K2[{start}:{start + 97}]", "expected": "KRYPTOS W/W vigenere p=8",
                    "recovered_p8": bool(ka_row in set(surv[8].tolist())),
                    "survivors_p8": int(len(surv[8])), "survivors_by_period_le24":
                    {p: int(len(v)) for p, v in surv.items() if p <= 24 and len(v)}})
    k1c, k1p = texts["K1_cipher"], texts["K1_plain"]
    positions = tuple(range(0, 13)) + tuple(range(42, 53))
    cribs = {i: k1p[i] for i in positions}
    cells = periodic_cells(positions)
    d = differences(pos, "W/W", "vigenere", k1c, cribs, positions)
    surv = periodic_survivors(d, cells)
    out.append({"control": "K1 cribs 0-12,42-52", "expected": "KRYPTOS W/W vigenere p=10",
                "recovered_p10": bool(ka_row in set(surv[10].tolist())),
                "survivors_p10": int(len(surv[10])),
                "survivors_by_period_le24": {p: int(len(v)) for p, v in surv.items() if p <= 24 and len(v)}})
    return out

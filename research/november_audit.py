"""Independent audit of the second Gemini Kryptos report.

Requires Python 3.9+ and NumPy. This is a bounded diagnostic, not a K4 solution.
No network or paid verifier access. Indices are zero based unless labeled.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import random
import time

import numpy as np

STD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
ANCHORS = dict(zip(range(21, 34), "EASTNORTHEAST")) | dict(zip(range(63, 74), "BERLINCLOCK"))
POSITIONS = tuple(ANCHORS)
GROUPS = defaultdict(list)
for _i, _p in ANCHORS.items():
    GROUPS[_p].append(_i)
PAIRS = [(i, j) for ids in GROUPS.values() for i, j in itertools.combinations(ids, 2)]
SYNTHETIC_PLAINTEXT = ("FROMTHEGATEYOUCANLOOK" + "EASTNORTHEAST"
                      + "TOSEETHEHIDDENMESSAGEBYTHEOLD" + "BERLINCLOCK"
                      + "ANDWAITFORTHENEXTSIGNAL")


def circular_span(values):
    """Shortest containing arc, measured in steps rather than number of slots."""
    v = sorted(set(values))
    return 0 if len(v) < 2 else 26 - max((v[(j + 1) % len(v)] - v[j]) % 26 for j in range(len(v)))


def required_shifts(alpha, mode, ciphertext=CT):
    out = {}
    for i, p in ANCHORS.items():
        c, p = alpha.index(ciphertext[i]), alpha.index(p)
        out[i] = {"vig": c - p, "beau": c + p, "vbeau": p - c}[mode] % 26
    return out


def phase_fit(shifts, period, relative):
    key = {}
    for i, k in shifts.items():
        r = (i + (relative if i >= 63 else 0)) % period
        if r in key and key[r] != k:
            return None
        key[r] = k
    return {"distinct_anchor_residues": len(key), "collisions": 24 - len(key),
            "free_key_residues": period - len(key), "key_partial": key}


def phase_audit():
    rows = []
    checks = 0
    for name, alpha in [("STD", STD), ("KRY", KRY)]:
        for mode in ("vig", "beau", "vbeau"):
            shifts = required_shifts(alpha, mode)
            matches = []
            for period in range(1, 27):
                for relative in range(period):
                    checks += 1
                    result = phase_fit(shifts, period, relative)
                    if result is not None:
                        matches.append({"period": period, "relative_phase_added_to_second_block": relative, **result})
            assert min(r["period"] for r in matches) == 24
            assert all(r["collisions"] == 0 for r in matches)
            gaps = {n: [p for p in range(1, 27) if phase_fit(shifts, p, -n) is not None]
                    for n in range(5)}
            assert gaps == {0: [], 1: [26], 2: [26], 3: [25, 26], 4: [25]}
            rows.append({"alphabet": name, "mode": mode, "compatible_phases": matches,
                         "compatible_periods_for_gap_null_count": gaps})
    assert checks == 2106
    # Positive tests: true period-7 models with skips must be retained by the same phase checker.
    controls = []
    for name, alpha in [("STD", STD), ("KRY", KRY)]:
        key = [1, 4, 2, 8, 5, 7, 3]
        for gap in range(5):
            synthetic = list("A" * 97)
            for i, p in ANCHORS.items():
                effective = i - (gap if i >= 63 else 0)
                synthetic[i] = alpha[(alpha.index(p) + key[effective % 7]) % 26]
            fit = phase_fit(required_shifts(alpha, "vig", "".join(synthetic)), 7, -gap)
            assert fit is not None
            controls.append({"alphabet": name, "gap": gap, "true_period": 7, "retained": True})
    return {"checks": checks, "models": rows, "positive_controls": controls,
            "scope": "No change inside either crib block; only a constant relative phase change between blocks. No other substitution alphabet or transposition."}


def arbitrary_alphabet_fit(period, alpha, unknown_side, ciphertext=CT):
    """Complete modular graph solver for one arbitrary permutation alphabet.

    X(letter)-Y(key residue)=known_value modulo 26. Cycle consistency fixes
    relative node values within components. Each component has one translation.
    Exhaustively assign translations and require distinct X values. Any partial
    injection on observed letters extends to a permutation of all 26 letters.
    """
    adj = defaultdict(list)
    edges = set()
    for i, p in ANCHORS.items():
        letter = p if unknown_side == "PT" else ciphertext[i]
        value = alpha.index(ciphertext[i] if unknown_side == "PT" else p)
        x, y = ("X", letter), ("Y", i % period)
        adj[x].append((y, -value))
        adj[y].append((x, value))
        edges.add((x, y, value))
    seen, components = {}, []
    for node in adj:
        if node in seen:
            continue
        seen[node] = 0
        queue, xs = [node], {}
        for u in queue:
            if u[0] == "X":
                xs[u[1]] = seen[u]
            for v, delta in adj[u]:
                value = (seen[u] + delta) % 26
                if v in seen:
                    if seen[v] != value:
                        return None
                else:
                    seen[v] = value
                    queue.append(v)
        if len(set(xs.values())) != len(xs):
            return None
        components.append(xs)
    components.sort(key=lambda x: -len(x))
    masks = [[sum(1 << ((v + off) % 26) for v in comp.values()) for off in range(26)] for comp in components]

    def search(j, occupied):
        if j == len(masks):
            return []
        # One global rotation is immaterial, so fix the first component at 0.
        for off, mask in enumerate(masks[j] if j else masks[j][:1]):
            if occupied & mask:
                continue
            tail = search(j + 1, occupied | mask)
            if tail is not None:
                return [off] + tail
        return None

    offsets = search(0, 0)
    if offsets is None:
        return None
    mapping = {ch: (v + off) % 26 for comp, off in zip(components, offsets) for ch, v in comp.items()}
    key = {}
    for i, p in ANCHORS.items():
        k = ((alpha.index(ciphertext[i]) - mapping[p]) if unknown_side == "PT"
             else (mapping[ciphertext[i]] - alpha.index(p))) % 26
        if i % period in key:
            assert key[i % period] == k
        key[i % period] = k
    assert len(set(mapping.values())) == len(mapping)
    return {"period": period, "components": len(components),
            "cycle_rank_after_identical_edge_deduplication": len(edges) - len(adj) + len(components),
            "witness_partial_alphabet": mapping, "witness_partial_key": key}


def alphabet_graph_audit():
    results = []
    for side in ("PT", "CT"):
        for name, alpha in [("STD", STD), ("KRY", KRY)]:
            hits = [arbitrary_alphabet_fit(p, alpha, side) for p in range(1, 27)]
            hits = [x for x in hits if x is not None]
            results.append({"unknown_alphabet": side, "fixed_alphabet": name,
                            "compatible_periods": [x["period"] for x in hits], "witnesses": hits})
    union = set().union(*(set(x["compatible_periods"]) for x in results))
    eliminated = sorted(set(range(1, 27)) - union)
    assert eliminated == list(range(1, 13)) + [14, 15, 17, 18, 21, 22, 25]
    rng = random.Random(20261123)
    controls = []
    for side in ("PT", "CT"):
        for name, alpha in [("STD", STD), ("KRY", KRY)]:
            for period in (1, 3, 7, 13, 20):
                mixed = list(STD)
                rng.shuffle(mixed)
                mixed = "".join(mixed)
                key = [rng.randrange(26) for _ in range(period)]
                cipher = "".join(alpha[(mixed.index(p) + key[i % period]) % 26] if side == "PT"
                                 else mixed[(alpha.index(p) + key[i % period]) % 26]
                                 for i, p in enumerate(SYNTHETIC_PLAINTEXT))
                assert arbitrary_alphabet_fit(period, alpha, side, cipher) is not None
                controls.append({"unknown_alphabet": side, "fixed_alphabet": name, "period": period, "retained": True})
    return {"graph_checks": 104, "models": results, "universally_excluded_periods_in_these_four_models": eliminated,
            "synthetic_controls": controls,
            "mode_equivalence_note": "With one fully arbitrary permutation alphabet and unrestricted periodic key values, sign changes absorb the three additive variants. This statement does not cover bounded numeric key alphabets."}


def parity_and_span_audit():
    parity = {p: sorted({(i + 1 + STD.index(CT[i])) % 2 for i in ids}) for p, ids in GROUPS.items()}
    assert all(len(x) == 1 for x in parity.values()) and len(PAIRS) == 13
    odd = sorted(p for p, v in parity.items() if v == [1])
    even = sorted(p for p, v in parity.items() if v == [0])
    span_tables, modular = {}, {}
    for name, alpha in [("STD", STD), ("KRY", KRY)]:
        table = []
        for slope in range(26):
            spans = [circular_span([(alpha.index(CT[i]) - slope * i) % 26 for i in ids])
                     for ids in GROUPS.values() if len(ids) > 1]
            table.append({"slope": slope, "sum_span": sum(spans), "max_span": max(spans)})
        span_tables[name] = table
        modular[name] = [(m, a) for m in range(2, 14) for a in range(m)
                         if all(len({(alpha.index(CT[i]) + a * i) % m for i in ids}) == 1 for ids in GROUPS.values())]
    assert span_tables["STD"][0]["sum_span"] == 35 and span_tables["KRY"][0]["sum_span"] == 67
    assert min(span_tables["STD"], key=lambda x: x["sum_span"])["slope"] == 0
    assert modular == {"STD": [(2, 1)], "KRY": []}
    start = CT.index("DIAWINFBN")
    differences = [(STD.index(CT[i + 4]) - STD.index(CT[i])) % 26 for i in range(start, start + 5)]
    assert start == 55 and differences == [5] * 5
    shifted_groups = defaultdict(set)
    for i, p in ANCHORS.items():
        removed = sum(j < i and CT[j] == "W" for j in range(97))
        shifted_groups[p].add((i - removed + 1 + STD.index(CT[i])) % 2)
    return {"lag4_start_zero_based": start, "lag4_end_zero_based": start + 8, "lag4_differences": differences,
            "odd_group_1based": odd, "even_group_1based": even, "matching_pairs": len(PAIRS),
            "independent_same_plaintext_comparisons": sum(len(v) - 1 for v in GROUPS.values()),
            "modulus_slope_hits": modular, "circular_span_tables": span_tables,
            "W_removal_breaks_groups": sorted(p for p, v in shifted_groups.items() if len(v) > 1),
            "first_two_standard_vigenere_key_values": [required_shifts(STD, "vig")[i] for i in [21, 22]],
            "direct_key_warning": "The first two adjacent known key values are 1 and 11, both odd; observed parity does not imply an alternating direct standard-alphabet keystream."}


def reverse_order_counterexample():
    # Existence example only: freely fitted key values, not a proposed K4 method.
    by_cipher = defaultdict(list)
    for i, p in ANCHORS.items():
        by_cipher[CT[i]].append((i, p))
    required = {ch: {(STD.index(p) + i) % 2 for i, p in entries} for ch, entries in by_cipher.items()}
    assert all(len(x) == 1 for x in required.values())
    available = {b: iter(range(b, 26, 2)) for b in (0, 1)}
    inverse = {ch: next(available[next(iter(required[ch]))]) for ch in sorted(required)}
    for ch, number in zip(sorted(set(STD) - set(inverse)), sorted(set(range(26)) - set(inverse.values()))):
        inverse[ch] = number
    outer = [""] * 26
    for ch, number in inverse.items():
        outer[number] = ch
    outer = "".join(outer)
    key = {i: (inverse[CT[i]] - STD.index(p)) % 26 for i, p in ANCHORS.items()}
    assert all(key[i] % 2 == i % 2 and outer[(STD.index(p) + key[i]) % 26] == CT[i] for i, p in ANCHORS.items())
    return {"not_a_solution": True, "order": "shift_then_substitute", "outer_alphabet": outer,
            "anchor_key_values": key, "anchor_matches": 24, "alternating_key_parity_at_anchors": True,
            "meaning": "Existence at one fitted key does not imply a pattern holds for every allowed key. Does not contradict the source's conditional universal theorem."}


def lfsr_audit():
    rows, period_counts = [], Counter()
    for mask in range(1, 32):
        for seed in range(1, 32):
            seq = [(seed >> b) & 1 for b in range(5)]
            for t in range(5, 180):
                seq.append(sum(((mask >> b) & 1) * seq[t - 5 + b] for b in range(5)) % 2)
            period = next((p for p in range(1, 32) if all(seq[t] == seq[t + p] for t in range(100))), None)
            period_counts[str(period)] += 1
            pair_fit = all((seq[i] ^ seq[j]) == ((STD.index(CT[i]) ^ STD.index(CT[j])) & 1) for i, j in PAIRS)
            if pair_fit:
                eventual = next(p for p in range(1, 32) if all(seq[t] == seq[t + p] for t in range(40, 140)))
                rows.append({"mask": mask, "seed": seed, "period_from_start": period,
                             "eventual_period": eventual,
                             "strict_alternation_on_all_anchors": len({seq[i] ^ (i % 2) for i in POSITIONS}) == 1})
    assert rows and all(r["eventual_period"] == 2 for r in rows)
    assert all(r["strict_alternation_on_all_anchors"] for r in rows)
    return {"configurations": 961, "definition": "Homogeneous binary order-at-most-five recurrences; nonzero feedback masks and nonzero initial states",
            "period_counts": dict(period_counts), "anchor_pair_survivors": rows,
            "genuine_period21_survivors": sum(r["period_from_start"] == 21 for r in rows),
            "limitation": "Does not establish that the observed width-21 bigrams were generated by an LFSR."}


def recurrence(primer, base):
    seq = list(primer)
    while len(seq) < 97:
        seq.append((seq[-5] + seq[-4]) % base)
    return seq


def recurrence_key_matrix(primers, base):
    coeff = np.zeros((97, 5), dtype=np.int16)
    coeff[:5] = np.eye(5, dtype=np.int16)
    for i in range(5, 97):
        coeff[i] = (coeff[i - 5] + coeff[i - 4]) % base
    return (primers @ coeff[np.array(POSITIONS)].T) % base


def scan_recurrence_keys(keys, side, alpha, sign, ciphertext):
    labels = "".join(ANCHORS.values()) if side == "PT" else "".join(ciphertext[i] for i in POSITIONS)
    fixed = np.array([alpha.index(ciphertext[i] if side == "PT" else ANCHORS[i]) for i in POSITIONS])
    maps = (fixed[None, :] - sign * keys) % 26 if side == "PT" else (fixed[None, :] + sign * keys) % 26
    groups = defaultdict(list)
    for j, letter in enumerate(labels):
        groups[letter].append(j)
    ok = np.ones(keys.shape[0], dtype=bool)
    for ids in groups.values():
        for j in ids[1:]:
            ok &= maps[:, j] == maps[:, ids[0]]
    equalities = int(ok.sum())
    first = [v[0] for v in groups.values()]
    for n, j in enumerate(first):
        for k in first[:n]:
            ok &= maps[:, j] != maps[:, k]
    return equalities, np.flatnonzero(ok)


def gromark_base12_audit():
    start = time.monotonic()
    base, count = 12, 12 ** 5
    numbers = np.arange(count, dtype=np.int32)
    primers = np.stack([(numbers // base ** j) % base for j in range(5)], axis=1)
    keys = recurrence_key_matrix(primers, base)
    cases = [("PT", "STD", STD), ("PT", "KRY", KRY), ("CT", "STD", STD)]
    rows, positives = [], []
    planted = [1, 2, 3, 4, 5]
    planted_seq = recurrence(planted, base)
    tiny_primers = np.array([planted, [0] * 5, [1] * 5], dtype=np.int32)
    tiny_keys = recurrence_key_matrix(tiny_primers, base)
    assert tiny_keys[0].tolist() == [planted_seq[i] for i in POSITIONS]
    mixed = "QWERTYUIOPASDFGHJKLZXCVBNM"
    for side, name, alpha in cases:
        for sign in (1, -1):
            eq, hits = scan_recurrence_keys(keys, side, alpha, sign, CT)
            assert len(hits) == 0
            rows.append({"unknown_alphabet": side, "fixed_alphabet": name, "sign": sign,
                         "primers": count, "equality_survivors": eq, "injective_survivors": len(hits)})
            synthetic = "".join(alpha[(mixed.index(p) + sign * planted_seq[i]) % 26] if side == "PT"
                                else mixed[(alpha.index(p) + sign * planted_seq[i]) % 26]
                                for i, p in enumerate(SYNTHETIC_PLAINTEXT))
            _, positive_hits = scan_recurrence_keys(tiny_keys, side, alpha, sign, synthetic)
            assert 0 in positive_hits
            positives.append({"unknown_alphabet": side, "fixed_alphabet": name, "sign": sign, "planted_primer_retained": True})
    return {"recurrence": "k[i]=(k[i-5]+k[i-4]) mod 12", "primer_values_including_leading_zero": "0..11",
            "primer_count": count, "model_primer_checks": count * len(rows), "models": rows,
            "positive_controls": positives, "elapsed_seconds": time.monotonic() - start,
            "scope": "Only fixed standard taps (5,4), length-five primers, six stated additive models, original positional correspondence. No transposition or nulls. No tests of Gemini's unspecified five other tap pairs."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=Path(__file__).with_name("audit_results.json"))
    args = ap.parse_args()
    assert len(CT) == 97 and len(SYNTHETIC_PLAINTEXT) == 97
    result = {"status": "Independent bounded follow-up audit, not a K4 solution",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "ciphertext": CT, "anchors": ANCHORS,
              "parity_and_spans": parity_and_span_audit(),
              "relative_phase_audit": phase_audit(),
              "arbitrary_alphabet_graph_audit": alphabet_graph_audit(),
              "reversed_order_existence_counterexample": reverse_order_counterexample(),
              "binary_lfsr_audit": lfsr_audit(),
              "base12_standard_taps_audit": gromark_base12_audit(),
              "not_performed": ["Original 61.8 million sweep reproduction", "721.7B community archive reproduction", "Lean toolchain proof checking",
                                "100,000 keyword Gromark campaign", "English quadgram scoring", "Paid verifier submission"]}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "lag4_start_0": result["parity_and_spans"]["lag4_start_zero_based"],
                      "parity_pair_matches": 13, "phase_checks": result["relative_phase_audit"]["checks"],
                      "no_phase_survivors_at_periods": "1..23",
                      "unknown_alphabet_graph_checks": result["arbitrary_alphabet_graph_audit"]["graph_checks"],
                      "lfsr_checks": 961, "base12_model_primer_checks": result["base12_standard_taps_audit"]["model_primer_checks"],
                      "base12_survivors": 0, "synthetic_controls_passed": 36}, indent=2))


if __name__ == "__main__":
    main()

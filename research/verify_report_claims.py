"""Independent, bounded checks of the supplied Gemini K4 report.

This does not implement or reproduce the report's large search campaign.
Python standard library only. The synthetic message is NOT a K4 proposal.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

STD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRY = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ANCHORS = dict(zip(range(21, 34), "EASTNORTHEAST")) | dict(zip(range(63, 74), "BERLINCLOCK"))
CANONICAL_K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"


def transform(text, key, alphabet, decrypt=False):
    result = []
    j = 0
    for ch in text:
        if ch not in alphabet:
            result.append(ch)
            continue
        sign = -1 if decrypt else 1
        result.append(alphabet[(alphabet.index(ch) + sign * alphabet.index(key[j % len(key)])) % 26])
        j += 1
    return "".join(result)


def rotate(text, columns, clockwise):
    assert len(text) % columns == 0
    rows = len(text) // columns
    if clockwise:
        return "".join(text[r * columns + c] for c in range(columns) for r in range(rows - 1, -1, -1))
    return "".join(text[r * columns + c] for c in range(columns - 1, -1, -1) for r in range(rows))


def period_check(ciphertext, pa, ca, mode):
    shifts = {}
    for i, plain in ANCHORS.items():
        c, p = ca.index(ciphertext[i]), pa.index(plain)
        shifts[i] = {"vig": c - p, "beau": c + p, "vbeau": p - c}[mode] % 26
    outcomes = []
    for period in range(1, 31):
        assigned = {}
        conflicts = []
        for i, v in shifts.items():
            r = i % period
            if r in assigned and assigned[r] != v:
                conflicts.append(i + 1)
            else:
                assigned[r] = v
        outcomes.append({"period": period, "compatible": not conflicts,
                         "distinct_anchor_residues": len({i % period for i in shifts}),
                         "conflicting_positions_1_based": conflicts})
    return {"anchor_shifts": shifts, "period_checks": outcomes,
            "compatible_periods_1_to_30": [x["period"] for x in outcomes if x["compatible"]]}


def rectangle_inventory(text):
    """Ordinary axis-aligned rectangles, not a test of symmetric margins."""
    found = []
    for width in range(3, 49):
        for letter in sorted(set(text)):
            cells = {(i // width, i % width) for i, ch in enumerate(text) if ch == letter}
            rectangles = set()
            for (r1, c1), (r2, c2) in itertools.combinations(cells, 2):
                if r1 != r2 and c1 != c2 and (r1, c2) in cells and (r2, c1) in cells:
                    rectangles.add(tuple(sorted(((r1, c1), (r1, c2), (r2, c1), (r2, c2)))))
            for rect in sorted(rectangles):
                found.append({"width": width, "letter": letter,
                              "corners_1_based": [[r + 1, c + 1] for r, c in rect]})
    return found


def synthetic_collision_counterexample():
    # Every element is specified before encryption. No K4 plaintext is inferred.
    plain = ("FROMTHEGATEYOUCANLOOK" + "EASTNORTHEAST"
             + "TOSEETHEHIDDENMESSAGEBYTHEOLD" + "BERLINCLOCK"
             + "ANDWAITFORTHENEXTSIGNAL")
    assert len(plain) == 97 and all(plain[i] == p for i, p in ANCHORS.items())
    cuts = [0, 21, 37, 49, 59, 75, 97]
    block_order = [1, 0, 2, 3, 5, 4]
    blocks = [list(range(a, b)) for a, b in zip(cuts, cuts[1:])]
    gather = list(itertools.chain.from_iterable(blocks[i] for i in block_order))
    inverse = [0] * 97
    for j, i in enumerate(gather):
        inverse[i] = j
    key = "ABCDEFGHIJKLMNOPQRSTUVWX"
    transposed = "".join(plain[i] for i in gather)
    cipher = transform(transposed, key, STD)
    recovered_intermediate = transform(cipher, key, STD, decrypt=True)
    recovered = "".join(recovered_intermediate[inverse[i]] for i in range(97))
    distinct = len({inverse[i] % len(key) for i in ANCHORS})
    collisions = len(ANCHORS) - distinct
    assert recovered == plain and collisions == 0
    return {"synthetic_only_not_a_k4_candidate": True,
            "purpose": "Demonstrate a false negative from a universal >=3 anchor collision gate",
            "order": "transposition_then_substitution", "alphabet": STD,
            "plaintext": plain, "ciphertext": cipher, "key": key,
            "fixed_partition_boundaries": cuts, "block_order_zero_based": block_order,
            "roundtrip_exact": recovered == plain, "anchor_matches": 24,
            "distinct_anchor_residues": distinct, "anchor_collisions": collisions,
            "would_fail_at_least_three_collision_gate": collisions < 3,
            "scope_note": "Explicit block permutation; does not reproduce Gemini's unpublished permutation generator."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1] / "docs/archive/legacy_kryptos_analysis.py")
    ap.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "out/local/independently_checked.json")
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location("legacy", args.source)
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    cipher = legacy.K4_CIPHERTEXT
    assert cipher == CANONICAL_K4
    k1_plain = transform(legacy.K1_CIPHERTEXT, "PALIMPSEST", KRY, decrypt=True)
    expected_k1 = legacy.clean_text(legacy.K1_PLAINTEXT)
    assert k1_plain == expected_k1
    k2_raw = legacy.K2_CIPHERTEXT
    assert k2_raw[358:364] == "NUPLGE"
    k2_corrected = k2_raw[:364] + "S" + k2_raw[364:]
    k2_plain_raw = transform(k2_raw, "ABSCISSA", KRY, decrypt=True)
    k2_plain_intended = transform(k2_corrected, "ABSCISSA", KRY, decrypt=True)
    assert legacy.clean_text(k2_plain_intended) == legacy.clean_text(legacy.K2_PLAINTEXT)
    k3_letters = legacy.clean_text(legacy.K3_CIPHERTEXT)
    k3_plain = rotate(rotate(k3_letters, 24, False), 8, False)
    assert k3_plain == legacy.clean_text(legacy.K3_PLAINTEXT)
    k3_reencrypted = rotate(rotate(k3_plain, 42, True), 14, True)
    assert k3_reencrypted == k3_letters
    variants = []
    for name, pa, ca, modes in [("STD", STD, STD, ("vig", "beau", "vbeau")),
                                ("KRY", KRY, KRY, ("vig", "beau", "vbeau")),
                                ("Q1_fixed_orientation", KRY, STD, ("vig",)),
                                ("Q2_fixed_orientation", STD, KRY, ("vig",))]:
        for mode in modes:
            result = period_check(cipher, pa, ca, mode)
            assert result["compatible_periods_1_to_30"] == [27, 28, 29]
            variants.append({"name": name + "_" + mode, "plaintext_alphabet": pa,
                             "ciphertext_alphabet": ca, **result})
    anchor_set = set(ANCHORS)
    groups = {"anchor_only": [], "unknown_only": [], "mixed": []}
    for i in range(94):
        window = set(range(i, i + 4))
        group = "anchor_only" if window <= anchor_set else "unknown_only" if not window & anchor_set else "mixed"
        groups[group].append(i)
    assert [len(groups[k]) for k in ("anchor_only", "unknown_only", "mixed")] == [18, 64, 12]
    counts = Counter(cipher)
    reported_counts = [55792512, 3119976, 1797840, 461088, 451398, 49600, 37860, 23728, 19968]
    result = {
        "status": "Independent bounded audit; large Gemini campaign NOT reproduced",
        "input_source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "k4_ciphertext": cipher, "k4_letter_counts": dict(sorted(counts.items())),
        "k4_ic": sum(v * (v - 1) for v in counts.values()) / (97 * 96),
        "baseline_checks": {
            "k1_expected_plaintext": k1_plain == expected_k1,
            "k1_roundtrip": transform(k1_plain, "PALIMPSEST", KRY) == legacy.K1_CIPHERTEXT,
            "k2_carved_tail": k2_plain_raw[-30:], "k2_intended_tail": k2_plain_intended[-30:],
            "k2_carved_roundtrip": transform(k2_plain_raw, "ABSCISSA", KRY) == k2_raw,
            "k2_intended_roundtrip": transform(k2_plain_intended, "ABSCISSA", KRY) == k2_corrected,
            "k3_expected_plaintext_letters": k3_plain == legacy.clean_text(legacy.K3_PLAINTEXT),
            "k3_roundtrip_letters": k3_reencrypted == k3_letters,
            "k3_punctuation_policy": "336 letters rotated; final physical question mark is retained separately",
        },
        "direct_period_test_count": len(variants) * 30,
        "direct_period_scope": "Fixed alphabets and additive equations, direct positional alignment, no transposition",
        "direct_period_variants": variants,
        "quadgram_window_counts": {k: len(v) for k, v in groups.items()},
        "quadgram_window_starts_zero_based": groups,
        "reported_sweep_arithmetic_only": {
            "rows": reported_counts, "sum": sum(reported_counts),
            "after_removing_reported_p24_overlap": sum(reported_counts) - 14982 * 12,
            "semantic_uniqueness_not_established": True,
        },
        "reported_p24_survivor_completion_count_if_distribution_is_correct": {
            "zero_collision_models": 396, "one_collision_models": 66,
            "free_key_letters_in_one_collision_period24_model": 1,
            "possible_completions_including_all_26_fills": 396 + 66 * 26,
            "note": "Conditional arithmetic, not independent reproduction of 462 survivors",
        },
        "synthetic_collision_counterexample": synthetic_collision_counterexample(),
        "ordinary_rectangle_inventory": rectangle_inventory(cipher),
        "geometry_scope_note": "Ordinary rectangles are not the same criterion as four symmetrically inset corners of a specified grid",
        "limitations": ["No new large cipher sweep", "No quadgram corpus supplied or new language scoring performed",
                        "No paid verifier submission", "No confirmation of Gemini's source code, run logs or runtime measurements"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "baseline_checks": result["baseline_checks"],
                      "direct_period_test_count": result["direct_period_test_count"],
                      "quadgram_window_counts": result["quadgram_window_counts"],
                      "synthetic_collision_counterexample_roundtrip": result["synthetic_collision_counterexample"]["roundtrip_exact"]}, indent=2))


if __name__ == "__main__":
    main()

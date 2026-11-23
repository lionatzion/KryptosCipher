"""Run the 2026-10-07 audit and bounded attacks. No network or third-party packages."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import heapq
import json
from math import prod
from pathlib import Path
import time

from kryptos_k4_p27_sweep import EN_LETTER_FREQ, COMMON_BIGRAMS, FUNC_WORDS

from research.k4_core import (
    ABC, KA, CIPHER, CRIBS, ALPHABETS, candidate_check, decrypt, encrypt,
    feedback_constraints, implied_keys, periodic_constraints, recurrence_candidates, systems,
)

ROOT = Path(__file__).resolve().parents[1]
SCORE_WEIGHTS = {2: Counter(), 3: Counter()}
for _word in COMMON_BIGRAMS:
    SCORE_WEIGHTS[len(_word)][_word] += 1
for _word in FUNC_WORDS:
    SCORE_WEIGHTS[len(_word)][_word] += 3
SCORE_WINDOWS = {n: [i for i in range(98-n) if all(j not in CRIBS for j in range(i, i+n))]
                 for n in SCORE_WEIGHTS}
SCORE_LETTERS = [i for i in range(97) if i not in CRIBS]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def legacy_audit():
    names = ["k4_top10_summary.json", "data/exports/k4_top10_summary.json",
             "k4_top100_candidates_light.csv", "data/exports/k4_top100_candidates_light.csv",
             "kryptos_k4_top50_period27.csv", "kryptos_k4_top100_period27_quadgram_composite.csv",
             "Top_5_K4_candidates_with_highlighted_phrases.csv"]
    results = []
    for name in names:
        path = ROOT / name
        rows = json.loads(path.read_text()) if path.suffix == ".json" else list(
            csv.DictReader(path.open()))
        counts, examples = Counter(), {}
        for raw in rows:
            row = {k.lower(): v for k, v in raw.items()}
            plain, key = row.get("plaintext"), row.get("keystream_27")
            if not plain or not key:
                status = "missing_plaintext_or_key"
                phases = []
            elif len(plain) != 97 or len(key) != 27 or set(plain + key) - set(ABC):
                status = "invalid_length_or_characters"
                phases = []
            else:
                phases = [j for j in range(27) if decrypt(CIPHER,
                          [ABC.index(key[(i + j) % 27]) for i in range(97)]) == plain]
                status = "exact_phase0" if 0 in phases else (
                    "requires_unrecorded_phase" if phases else "does_not_reproduce")
            counts[status] += 1
            examples.setdefault(status, {"matching_phases": phases,
                                          "plaintext_length": len(plain) if plain else None})
        results.append({"file": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "rows": len(rows), "classifications": dict(counts), "examples": examples})
    return results


def period_audit():
    tracks = {}
    for name, pa, ca, a in systems():
        keys = implied_keys(pa=pa, ca=ca, a=a)
        rows = []
        for period in range(1, 98):
            values, conflicts = periodic_constraints(keys, period)
            rows.append({"period": period, "known_residues": len(values),
                         "independent_repeat_checks": len(keys) - len(values),
                         "unknown_residues": period - len(values),
                         "compatible": not conflicts,
                         "first_conflict": conflicts[0] if conflicts else None})
        tracks[name] = {"compatible_periods": [r["period"] for r in rows if r["compatible"]]}
        if name in ("P=ABC;C=ABC;a=1", "P=ABC;C=ABC;a=25"):
            tracks[name]["details"] = rows
    keys = implied_keys()
    cycle, _ = periodic_constraints(keys, 27)
    template = decrypt(CIPHER, [cycle.get(i % 27, 0) for i in range(97)])
    template = "".join(c if i % 27 in cycle else "?" for i, c in enumerate(template))
    return {"tracks": tracks, "standard_p27": {
        "key_template_0b": "".join(ABC[cycle[i]] if i in cycle else "?" for i in range(27)),
        "unknown_residues_0b": sorted(set(range(27)) - set(cycle)),
        "forced_plaintext": template, "forced_characters": 97 - template.count("?"),
        "fit_parameters": len(cycle), "independent_repeat_checks": 24 - len(cycle),
        "shift_zero_positions_1b": [i + 1 for i, k in keys.items() if k == 0],
        "all_fills": 26 ** (27 - len(cycle)),
        "note": "Zero shifts at 33/74 are already implied by the cribs, not additional clues."}}


def progressive_attack():
    """All periods <=26, wheel phases, additive drift, and 48 affine alphabet systems."""
    counts = defaultdict(Counter)
    examples, canonical = [], []
    for name, pa, ca, a in systems():
        keys = implied_keys(pa=pa, ca=ca, a=a)
        for period in range(1, 27):
            for phase in range(period):
                for drift in range(26):
                    counts[period]["tested"] += 1
                    values, conflicts = periodic_constraints(keys, period, phase, drift)
                    if not conflicts:
                        counts[period]["compatible"] += 1
                        if phase == 0:
                            canonical.append({"system": name, "period": period,
                                              "drift": drift, "base": values,
                                              "pa": pa, "ca": ca, "a": a})
                        if len(examples) < 12:
                            examples.append({"system": name, "period": period,
                                             "phase": phase, "drift": drift,
                                             "unknown_residues": period - len(values),
                                             "independent_repeat_checks": 24 - len(values)})
    return {"tested": sum(c["tested"] for c in counts.values()),
            "compatible": sum(c["compatible"] for c in counts.values()),
            "by_period": dict(counts), "first_12_compatible": examples,
            "canonical_phase0_models": canonical,
            "scope": "K_i=B[(i+h)%m]+d*floor((i+h)/m), m=1..26, h=0..m-1, d=0..25. "
                     "Free B, four ABC/KRYPTOS plaintext/ciphertext alphabet pairs, all 12 unit "
                     "plaintext multipliers. No transposition. Compatible does not mean English."}


def recurrence_attack():
    rows = []
    for name, pa, ca, a in systems():
        for order in range(1, 9):
            result = recurrence_candidates(implied_keys(pa=pa, ca=ca, a=a), order)
            result["system"] = name
            rows.append(result)
    return {"scope": "All affine homogeneous-in-time recurrences of orders 1..8 modulo 26, "
                     "with arbitrary initial states and constant term; 48 alphabet/multiplier systems. "
                     "Local crib equations solved over GF(2) and GF(13), CRT combined and "
                     "propagated from the first crib block to the second. Cap=100000 coefficient "
                     "vectors per system/order; capped cases stay open.",
            "systems_and_orders": len(rows),
            "coefficient_vectors_checked": sum(r["forward_checked"] for r in rows),
            "unresolved_capped": sum(not r["complete"] for r in rows),
            "surviving_coefficient_vectors": sum(len(r["survivors"]) for r in rows),
            "rows": rows}


def feedback_attack():
    counts, survivors, parameters = defaultdict(Counter), [], []
    # Four alphabet pairs, two signs on each plaintext term, every constant shift.
    for pn, pa in ALPHABETS.items():
        for cn, ca in ALPHABETS.items():
            for lag in range(1, 49):
                for a in (1, 25):
                    for b in (1, 25):
                        for shift in range(26):
                            counts[lag]["tested"] += 1
                            result = feedback_constraints(CIPHER, CRIBS, lag, a, b, shift, pa, ca)
                            if result is not None:
                                counts[lag]["compatible"] += 1
                                free = prod(len(v) for v in result["allowed_seed_values"])
                                parameters.append({"pa": pn, "ca": cn, "lag": lag, "a": a,
                                                   "b": b, "shift": shift, "seed_completions": free})
                                if len(survivors) < 12:
                                    survivors.append({"pa": pn, "ca": cn, "lag": lag, "a": a,
                                                      "b": b, "shift": shift,
                                                      "seed_completions": free,
                                                      "forced_plaintext": result["forced_plaintext"]})
    return {"scope": "C_i=a*P_i+b*P_(i-lag)+t (mod26) after an arbitrary lag-letter primer; "
                     "lag=1..48, a,b in {1,-1}, t=0..25, all four ABC/KRYPTOS alphabet pairs. "
                     "Primer is entirely free. Each residue chain's 26 starting values are "
                     "checked exactly; no language ranking or sampling.",
            "tested": sum(c["tested"] for c in counts.values()),
            "compatible": sum(c["compatible"] for c in counts.values()),
            "by_lag": dict(counts), "first_12_compatible": survivors,
            "surviving_parameters": parameters}


def blind_score(plain):
    """Legacy-style ranking restricted to non-crib characters and n-gram windows.

    Descriptive heuristic only. No calibrated probability, and no acceptance threshold.
    Contiguous windows that touch a crib are excluded to prevent crib-score leakage.
    """
    counts = Counter(plain[i] for i in SCORE_LETTERS)
    length = sum(counts.values())
    score = -0.5 * sum((counts[c] - pct / 100 * length) ** 2 / (pct / 100 * length)
                       for c, pct in EN_LETTER_FREQ.items())
    for n, weights in SCORE_WEIGHTS.items():
        score += sum(weights.get(plain[i:i+n], 0) for i in SCORE_WINDOWS[n])
    return score


def complete_progressive():
    """Complete all phase-deduplicated surviving progressive models, bounded by free cells."""
    from itertools import product
    models = progressive_attack()["canonical_phase0_models"]
    top, total, skipped, per_model = [], 0, [], []
    for model_id, model in enumerate(models):
        base = [model["base"].get(i) for i in range(model["period"])]
        free = [i for i, value in enumerate(base) if value is None]
        if len(free) > 3:
            skipped.append({"model_id": model_id, "unknown_residues": len(free)})
            continue
        best = None
        ca, pa, a = model["ca"], model["pa"], model["a"]
        # Fast precomputed decoding; each free residue changes at most four characters.
        inv = pow(a, -1, 26)
        tables = [[pa[((ca.index(CIPHER[i]) - k - model["drift"] *
                         (i // model["period"])) * inv) % 26] for i in range(97)]
                  for k in range(26)]
        fixed = [tables[base[i % model["period"]] or 0][i] for i in range(97)]
        for values in product(range(26), repeat=len(free)):
            letters = fixed[:]
            trial_base = base[:]
            for r, k in zip(free, values):
                trial_base[r] = k
                for i in range(r, 97, model["period"]):
                    letters[i] = tables[k][i]
            plain = "".join(letters)
            total += 1
            score = blind_score(plain)
            item = (score, plain, tuple(trial_base), model_id)
            if best is None or item > best:
                best = item
            if len(top) < 10:
                heapq.heappush(top, item)
            elif item > top[0]:
                heapq.heapreplace(top, item)
        per_model.append({"model_id": model_id, "tested": 26 ** len(free),
                          "best_score": best[0], "best_plaintext": best[1]})
    records = []
    for score, plain, base, model_id in sorted(top, reverse=True):
        model = models[model_id]
        key = [(base[i % model["period"]] + model["drift"] * (i // model["period"])) % 26
               for i in range(97)]
        generated = encrypt(plain, key, model["pa"], model["ca"], model["a"])
        check = candidate_check(plain, generated)
        assert check["consistent"]
        records.append({"score": score, "plaintext": plain, "base_key_numeric": base,
                        "model_id": model_id, "verification": check})
    return {"scope": "Exhaust all 26^u base keys when u<=3, for every surviving phase-zero "
                     "progressive model. Other phases are equivalent by relabeling base slots "
                     "and absorbing one drift where a slot wraps. Rank non-crib letters only. "
                     "Top results are diagnostics, not proposed solutions.",
            "tested_completions": total, "canonical_models": models,
            "skipped_models": skipped, "per_model": per_model, "top_10": records}


def source_texts():
    # Transcribed from Elonka Dunin's sculpture transcript, viewed 2026-10-07.
    # Question marks excluded (not letters); no other editorial changes.
    top = (
        "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
        "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKKDQMCPFQZDQMMIAGPFXHQRLG"
        "TIMVMZJANQLVKQEDAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCRTBJDFHRR"
        "YIZETKZEMVDUFKSJHKFWHKUWQLSZFTIHHDDDUVHDWKBFUFPWNTDFIYCUQZERE"
        "EVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTEZFKZBSFDQVGOGIPUFXHHDRKF"
        "FHQNTGPUAECNUVPDJMQCLQUMUNEDFQELZZVRRGKFFVOEEXBDMVPNFQXEZLGRE"
        "DNQFMPNZGLFLPMRJQYALMGNUVPDXVKPDQUMEBEDMHDAFMJGZNUPLGEWJLLAETG"
    )
    k3 = (
        "ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIACHTNREYULDSLLSLLNOHSNOSMRWXMNE"
        "TPRNGATIHNRARPESLNNELEBLPIIACAEWMTWNDITEENRAHCTENEUDRETNHAEOE"
        "TFOLSEDTIWENHAEIOYTEYQHEENCTAYCREIFTBRSPAMHHEWENATAMATEGYEERLB"
        "TEEFOASFIOTUETUAEOTOARMAEERTNRTIBSEDDNIAAHTTMSTEWPIEROAGRIEWFEB"
        "AECTDDHILCEIHSITEGOEAOSDDRYDLORITRKLMLEHAGTDHARDPNEOHMGFMFEUHE"
        "ECDMRIPFEIMEHNLSSTTRTVDOHW"
    )
    assert len(top) == 432 and len(k3) == 336
    k1, k2 = top[:63], top[63:]
    p1 = decrypt(k1, [KA.index("PALIMPSEST"[i % 10]) for i in range(63)], KA, KA)
    p2 = decrypt(k2, [KA.index("ABSCISSA"[i % 8]) for i in range(369)], KA, KA)
    assert p1.startswith("BETWEENSUBTLESHADING") and p1.endswith("IQLUSION")
    assert p2.startswith("ITWASTOTALLYINVISIBLE") and p2.endswith("IDBYROWS")
    return {"K1_cipher": k1, "K2_cipher": k2, "K3_cipher": k3,
            "K1_plain": p1, "K2_plain_as_inscribed": p2,
            "K1K2K3_cipher": top + k3, "K1K2_plain_as_inscribed": p1 + p2}


def running_key_attack():
    sources = source_texts()
    best, hits, tested = [], [], 0
    # A bounded sculpture-text hypothesis, not a general running-key search.
    for name, source in sources.items():
        for direction in (1, -1):
            for kn, ka in ALPHABETS.items():
                for system, pa, ca, a in systems():
                    required = implied_keys(pa=pa, ca=ca, a=a)
                    for offset in range(len(source)):
                        stream = [ka.index(source[(offset + direction * i) % len(source)])
                                  for i in range(97)]
                        # Exhaust all 26 uniform shifts together via a histogram.
                        shifts = Counter((k - stream[i]) % 26 for i, k in required.items())
                        tested += 26
                        shift, matches = shifts.most_common(1)[0]
                        row = {"source": name, "direction": direction, "key_alphabet": kn,
                               "system": system, "offset": offset, "shift": shift,
                               "anchor_matches": matches}
                        if matches == 24:
                            key = [(v + shift) % 26 for v in stream]
                            plain = decrypt(CIPHER, key, pa, ca, a)
                            row.update(plaintext=plain, verification=candidate_check(
                                plain, encrypt(plain, key, pa, ca, a)))
                            hits.append(row)
                        best.append(row)
                        if len(best) > 100:
                            best = sorted(best, key=lambda r: -r["anchor_matches"])[:10]
    return {"scope": "Seven sculpture-derived streams; every cyclic start; forward/backward; "
                     "ABC or KRYPTOS key indexing; all 48 affine alphabet systems; "
                     "all 26 uniform shifts. K2 is the as-inscribed decryption ending IDBYROWS; "
                     "the corrected XLAYERTWO variant and K3 plaintext are not tested.",
            "source_metadata": {n: {"length": len(s), "sha256": hashlib.sha256(s.encode()).hexdigest()}
                                for n, s in sources.items()},
            "tested_parameter_tuples": tested, "full_anchor_hits": hits,
            "top_10_partial_matches_not_candidates": sorted(best, key=lambda r: -r["anchor_matches"])[:10]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=ROOT / "out/astra_20261007")
    parser.add_argument("--only", choices=("audit", "progressive", "recurrence", "feedback", "running", "complete"))
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    tasks = {"audit": lambda: {"ciphertext": CIPHER,
              "ciphertext_sha256": hashlib.sha256(CIPHER.encode()).hexdigest(),
              "cribs_1b": {i + 1: p for i, p in CRIBS.items()},
              "period_audit": period_audit(), "legacy_exports": legacy_audit()},
             "progressive": progressive_attack, "recurrence": recurrence_attack,
             "feedback": feedback_attack, "running": running_key_attack,
             "complete": complete_progressive}
    for name, function in tasks.items():
        if args.only and name != args.only:
            continue
        start = time.perf_counter()
        result = function()
        write_json(args.outdir / f"{name}.json", result)
        print(json.dumps({"experiment": name, "seconds": round(time.perf_counter() - start, 3),
                          "output": str(args.outdir / f"{name}.json"),
                          "summary": {k: v for k, v in result.items()
                                      if isinstance(v, (int, bool))}}), flush=True)


if __name__ == "__main__":
    main()

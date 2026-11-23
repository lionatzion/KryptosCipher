"""Exact bounded progressive-key search; see docs/KEYWORD_PROGRESSIVE_PREREG.md."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from math import gcd
from pathlib import Path
import platform
import random
import time

import numpy as np

from research.opus_review import audit, keyword_tableau as kt
from research.opus_review.core import ABC, CRIBS, CRIB_POSITIONS, K4, KA, ROOT

DICTIONARY_SHA256 = "be41ad97963bf8dabedd5871d5d691596175269d540956b0f9965a885c2bbab9"
ALPHABET_COUNT = 617732
PERIODS = tuple(range(1, 25))
EXAMPLE_CAP = 100
NULL_SEEDS = tuple(range(20263007, 20263019))


def repeat_pairs(period, positions=CRIB_POSITIONS):
    """Spanning repeated-residue pairs: (later column, first column, cycle gap)."""
    first, pairs = {}, []
    for col, i in enumerate(positions):
        residue = i % period
        if residue in first:
            old = first[residue]
            pairs.append((col, old, i // period - positions[old] // period))
        else:
            first[residue] = col
    return pairs


def progressive_survivors(observed, period, positions=CRIB_POSITIONS):
    """All (row, drift) solutions; every base residue remains an arbitrary parameter."""
    pairs = repeat_pairs(period, positions)
    if not pairs:
        return [(row, drift) for row in range(len(observed)) for drift in range(26)]
    pivot = min(pairs, key=lambda pair: gcd(pair[2], 26))
    a, b, gap = pivot
    common = gcd(gap, 26)
    modulus = 26 // common
    delta = (observed[:, a] - observed[:, b]) % 26
    rows = np.flatnonzero(delta % common == 0)
    roots = (delta[rows] // common * pow(gap // common, -1, modulus)) % modulus
    hits = []
    for lift in range(common):
        keep = rows.copy()
        drifts = roots + lift * modulus
        for j, i, cycles in pairs:
            good = (observed[keep, j] - observed[keep, i] - drifts * cycles) % 26 == 0
            keep, drifts = keep[good], drifts[good]
            if not len(keep):
                break
        hits.extend((int(row), int(drift)) for row, drift in zip(keep, drifts))
    return hits


def scalar_survivors(observed, period, positions=CRIB_POSITIONS):
    """Independent reference: fit free base residues for each of all 26 drifts."""
    hits = []
    for row, values in enumerate(observed):
        for drift in range(26):
            base, valid = {}, True
            for i, value in zip(positions, values):
                residue = i % period
                fitted = (int(value) - drift * (i // period)) % 26
                if residue in base and base[residue] != fitted:
                    valid = False
                    break
                base[residue] = fitted
            if valid:
                hits.append((row, drift))
    return hits


def phase_zero_base(base, drift, phase):
    """Absorb a key phase into free base values without changing the drift."""
    period = len(base)
    return [(base[(r + phase) % period] + drift * ((r + phase) // period)) % 26
            for r in range(period)]


def schedule(base, drift, length, phase=0):
    period = len(base)
    return [(base[(i + phase) % period] + drift * ((i + phase) // period)) % 26
            for i in range(length)]


def describe_hit(row, drift, period, config, sign, observed, family, cipher,
                 cribs, positions, cipher_row=None):
    alphabets, sources = family
    pa, ca = kt.tableau(config, alphabets[row]) if config != "W1/W2" else (
        alphabets[row], alphabets[cipher_row])
    base = {}
    for i, value in zip(positions, observed):
        fitted = (int(value) - drift * (i // period)) % 26
        residue = i % period
        assert base.setdefault(residue, fitted) == fitted
    shifts = [(base[i % period] + drift * (i // period)) % 26 if i % period in base
              else None for i in range(len(cipher))]
    plain = kt.decrypt(cipher, shifts, pa, ca, sign)
    assert all(plain[i] == cribs[i] for i in positions)
    determined = [i for i, k in enumerate(shifts) if k is not None]
    forward = all(kt.encrypt(plain[i], [shifts[i]], pa, ca, sign) == cipher[i]
                  for i in determined)
    assert forward
    return {
        "config": config, "sign": sign, "period": period, "drift": drift,
        "plain_source": sources[row] if config.split("/")[0].startswith("W") else None,
        "cipher_source": sources[cipher_row if cipher_row is not None else row]
        if config.split("/")[1].startswith("W") else None,
        "plain_alphabet": pa, "cipher_alphabet": ca,
        "base_key": [base.get(r) for r in range(period)],
        "free_base_residues": [r for r in range(period) if r not in base],
        "determined_letters": len(determined), "partial_plaintext": plain,
        "forward_matches_determined": len(determined), "is_solution": False,
    }


def run_search(family, pos, cipher=K4, cribs=CRIBS, positions=CRIB_POSITIONS,
               periods=PERIODS, examples=True):
    """Complete declared search. Example caps do not affect counts or feasibility."""
    alphabets = family[0]
    contexts = kt.context_rows(family)
    left = np.repeat(contexts, len(contexts))
    right = np.tile(contexts, len(contexts))
    distinct = left != right
    left, right = left[distinct], right[distinct]
    counts, rows, stored, caps = Counter(), [], [], []
    tested_rows = 0
    for config in kt.CONFIGS + ("W1/W2",):
        for sign in kt.PERIODIC_SIGNS:
            if config == "W1/W2":
                observed = kt.differences(pos[left], "W/W", sign, cipher, cribs,
                                          positions, pos_c=pos[right])
            else:
                observed = kt.differences(pos, config, sign, cipher, cribs, positions)
            tested_rows += len(observed)
            for period in periods:
                hits = progressive_survivors(observed, period, positions)
                by_drift = Counter(d for _, d in hits)
                counts[period] += len(hits)
                rows.append({"config": config, "sign": sign, "period": period,
                             "survivors": len(hits),
                             "by_drift": {str(d): by_drift[d] for d in range(26)},
                             "alphabet_rows": len(observed)})
                if examples:
                    if len(hits) > EXAMPLE_CAP:
                        caps.append({"config": config, "sign": sign, "period": period,
                                     "survivors": len(hits), "stored": EXAMPLE_CAP})
                    for row, drift in hits[:EXAMPLE_CAP]:
                        stored.append(describe_hit(
                            int(left[row]) if config == "W1/W2" else row,
                            drift, period, config, sign, observed[row], family,
                            cipher, cribs, positions,
                            int(right[row]) if config == "W1/W2" else None))
    first_block = set(positions[:13])
    bookkeeping = {}
    for period in periods:
        residues = {i % period for i in positions}
        fitted = {i % period for i in first_block}
        bookkeeping[str(period)] = {
            "repeated_residue_congruences": len(positions) - len(residues),
            "first_block_internal_congruences": 13 - len(fitted),
            "second_block_positions_with_first_block_residue": sum(
                i % period in fitted for i in positions[13:]),
            "free_base_residues": period - len(residues),
            "drift_values_fitted": 26,
        }
    return {"period_counts": {str(p): counts[p] for p in periods}, "cells": rows,
            "bookkeeping": bookkeeping, "examples": stored, "example_caps": caps,
            "alphabet_config_sign_rows": tested_rows,
            "nominal_parameter_tuples": tested_rows * len(periods) * 26,
            "scope_complete": True, "is_solution": False}


def controls(family, pos):
    """Run scalar checks, genuine Sanborn controls, and 30 plants before the K4 search."""
    rng = random.Random(20261007)
    observed = np.array([[rng.randrange(26) for _ in CRIB_POSITIONS] for _ in range(12)],
                        dtype=np.int16)
    for period in PERIODS:
        assert sorted(progressive_survivors(observed, period)) == sorted(
            scalar_survivors(observed, period))
    texts, _, _ = audit.sculpture_texts()
    kryptos_row = family[0].index(KA)
    real = []
    for name, period, starts, positions in (
        ("K2", 8, (0, 50, 150, 250, 270), CRIB_POSITIONS),
        ("K1", 10, (0,), tuple(range(13)) + tuple(range(42, 53))),
    ):
        for start in starts:
            cipher = texts[name + "_cipher"][start:start + 97]
            plain_key = "K1_plain" if name == "K1" else "K2_plain_as_inscribed"
            plain = texts[plain_key][start:start + 97]
            cribs = {i: plain[i] for i in positions}
            values = kt.differences(pos, "W/W", "vigenere", cipher, cribs, positions)
            hits = progressive_survivors(values, period, positions)
            recovered = (kryptos_row, 0) in hits
            assert recovered
            real.append({"section": name, "start": start, "period": period,
                         "true_drift": 0, "recovered": recovered,
                         "compatible_row_drift_pairs": len(hits)})
    plants = []
    contexts = kt.context_rows(family)
    left = np.repeat(contexts, len(contexts))
    right = np.tile(contexts, len(contexts))
    distinct = left != right
    left, right = left[distinct], right[distinct]
    for n in range(30):
        config = (kt.CONFIGS + ("W1/W2",))[n % 6]
        sign = kt.PERIODIC_SIGNS[(n // 6) % 2]
        period = PERIODS[n % len(PERIODS)]
        drift = 0 if n % 7 == 0 else rng.randrange(1, 26)
        row = rng.randrange(len(family[0]))
        other = rng.choice(contexts) if config == "W1/W2" else None
        if config == "W1/W2":
            row = rng.choice([r for r in contexts if r != other])
            pa, ca = family[0][row], family[0][other]
        else:
            pa, ca = kt.tableau(config, family[0][row])
        phase = rng.randrange(period)
        base = [rng.randrange(26) for _ in range(period)]
        shifts = schedule(base, drift, 97, phase)
        assert schedule(phase_zero_base(base, drift, phase), drift, 97) == shifts
        plain = [rng.choice(ABC) for _ in range(97)]
        for i, ch in CRIBS.items():
            plain[i] = ch
        cipher = kt.encrypt("".join(plain), shifts, pa, ca, sign)
        if config == "W1/W2":
            observed = kt.differences(pos[left], "W/W", sign, cipher,
                                      pos_c=pos[right])
            expected_row = int(np.flatnonzero((left == row) & (right == other))[0])
        else:
            observed = kt.differences(pos, config, sign, cipher)
            expected_row = row
        full_hits = progressive_survivors(observed, period)
        assert (expected_row, drift) in full_hits
        values = observed[expected_row:expected_row + 1]
        hits = progressive_survivors(values, period)
        assert (0, drift) in hits
        assert sorted(hits) == sorted(scalar_survivors(values, period))
        pair = repeat_pairs(period)[0]
        tampered = values.copy()
        tampered[0, pair[0]] = (tampered[0, pair[0]] + 1) % 26
        assert (0, drift) not in progressive_survivors(tampered, period)
        assert kt.decrypt(cipher, shifts, pa, ca, sign) == "".join(plain)
        plants.append({"config": config, "sign": sign, "period": period,
                       "drift": drift, "phase": phase, "recovered": True,
                       "configuration_alphabet_rows_searched": len(observed),
                       "compatible_row_drift_pairs": len(full_hits),
                       "tampered_original_parameters_rejected": True,
                       "full_forward_matches": 97})
    return {"scalar_crosschecks": len(PERIODS), "real_controls": real,
            "plants": plants, "plants_recovered": len(plants), "all_passed": True}


def experiment(dictionary, log=print):
    started = time.monotonic()
    raw = dictionary.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != DICTIONARY_SHA256:
        raise ValueError("Dictionary hash differs from the registered input; scope not executed")
    prereg = ROOT / "docs/KEYWORD_PROGRESSIVE_PREREG.md"
    family = kt.alphabet_family(raw.decode().splitlines() + list(kt.CONTEXT_WORDS))
    if len(family[0]) != ALPHABET_COUNT:
        raise ValueError("Alphabet count differs from the registered input")
    pos = kt.positions_matrix(family[0])
    log("controls")
    checked = controls(family, pos)
    log("K4")
    result = run_search(family, pos)
    log("nulls")
    nulls = []
    for n, seed in enumerate(NULL_SEEDS, 1):
        cipher = "".join(random.Random(seed).sample(K4, 97))
        null = run_search(family, pos, cipher=cipher, examples=False)
        nulls.append({"seed": seed, "period_counts": null["period_counts"]})
        log(f"null {n}/{len(NULL_SEEDS)}")
    reference = {str(p): result["alphabet_config_sign_rows"] * 26 *
                 26.0 ** -len(repeat_pairs(p)) for p in PERIODS}
    return {
        "design_sha256": hashlib.sha256(prereg.read_bytes()).hexdigest(),
        "dictionary": {"filename": dictionary.name, "sha256": digest,
                       "nonempty_lines": sum(bool(w.strip()) for w in raw.decode().splitlines())},
        "family": {"alphabets": len(family[0]), "context_alphabets": len(kt.context_rows(family)),
                   "ordered_alphabet_sha256": hashlib.sha256(
                       "\n".join(family[0]).encode("ascii")).hexdigest(),
                   "modes": kt.MODES, "configs": kt.CONFIGS + ("W1/W2 context pairs",),
                   "signs": kt.PERIODIC_SIGNS, "periods": PERIODS, "drifts": list(range(26))},
        "controls": checked, "k4": result, "nulls": nulls,
        "uniform_independent_key_reference_expected_parameter_hits": reference,
        "reference_warning": "Reference assumes uniform independent implied key values. "
                             "Keyword alphabets and crib letter repetitions violate this model; "
                             "these numbers are not calibrated significance levels.",
        "null_mean_parameter_hits": {str(p): sum(x["period_counts"][str(p)] for x in nulls)
                                     / len(nulls) for p in PERIODS},
        "deviations": [
            "After the first K4 run, validation was strengthened: the initial 30 plants "
            "tested their true alphabet row; the final run searches each plant's full "
            "registered configuration at its true period. Both runs recover all plants. "
            "K4 scope, seeds, filters and interpretation did not change. "
            "initial_result.json and initial_run.log preserve the first run.",
        ], "seconds": round(time.monotonic() - started, 2),
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "no_additional_confirmed_plaintext": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dictionary", type=Path, default=kt.DICTIONARY)
    parser.add_argument("--outdir", type=Path, default=ROOT / "out/keyword_progressive_20261007")
    args = parser.parse_args()
    result = experiment(args.dictionary, log=lambda stage: print(stage, flush=True))
    outdir = args.outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    target = outdir / "result.json"
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"result": str(target.relative_to(ROOT)),
                      "period_counts": result["k4"]["period_counts"],
                      "seconds": result["seconds"]}), flush=True)


if __name__ == "__main__":
    main()

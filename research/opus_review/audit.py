"""Independent audit of the Astra K4 claims, plus alphabet-free generalizations.

Each function returns JSON-serializable evidence. Astra's code is imported only to
compare against committed results or to attack it with planted solutions.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
from itertools import product
import json
from math import comb, log2
import random

from research.opus_review.core import (
    ABC, BLOCKS, CRIBS, CRIB_POSITIONS, K4, KA, UNITS, QuagmireGraph, affine_keys,
    all_primers, crib_relations, decrypt_affine, encrypt_affine, lagged_fibonacci,
    periodic_any_alphabets, periodic_latin_square, solve_mod,
)
from research.opus_review.core import ROOT

ALPHABETS = {"ABC": ABC, "KRYPTOS": KA}


def systems():
    """The same 48 C=a*P+K systems Astra used, enumerated independently."""
    for (pn, pa), (cn, ca), a in product(ALPHABETS.items(), ALPHABETS.items(), UNITS):
        yield f"P={pn};C={cn};a={a}", pa, ca, a


def letters(values, alphabet=ABC):
    return "".join(alphabet[v] for v in values)


def committed(name):
    return json.loads((ROOT / "out/astra_20261007" / f"{name}.json").read_text())


# ------------------------------------------------------------------ inputs
def input_audit():
    from research import k4_core
    counts = Counter(K4)
    ic = Fraction(sum(n * (n - 1) for n in counts.values()), 97 * 96)
    vig = affine_keys()
    beau = affine_keys(a=25)
    kav = affine_keys(KA, KA)
    blocks = [[i for i in block] for block in BLOCKS]
    return {
        "ciphertext": K4, "sha256": hashlib.sha256(K4.encode()).hexdigest(),
        "matches_astra_cipher": K4 == k4_core.CIPHER,
        "matches_astra_cribs": CRIBS == k4_core.CRIBS,
        "crib_ciphertext_1b": {f"{b[0] + 1}-{b[-1] + 1}": "".join(K4[i] for i in b) for b in blocks},
        "letters_present": len(counts), "index_of_coincidence": f"{ic.numerator}/{ic.denominator}",
        "index_of_coincidence_float": round(float(ic), 5),
        "abc_vigenere_key_letters": [letters(vig[i] for i in b) for b in blocks],
        "abc_beaufort_key_letters": [letters(beau[i] for i in b) for b in blocks],
        "kryptos_vigenere_key_letters_KA": [letters((kav[i] for i in b), KA) for b in blocks],
        "self_encrypting_positions_1b": [i + 1 for i in CRIB_POSITIONS if K4[i] == CRIBS[i]],
        "note": "Self-encryption (C=P) at 33 and 74 is a fact about the cribs; under any "
                "tableau whose identity row is key 0 it implies key 0 there, nothing more.",
    }


# ------------------------------------------------------------ periodicity
def period_ladder(max_period=52, q4_samples=4000):
    """Which periods survive the cribs under progressively weaker alphabet assumptions."""
    graph = QuagmireGraph()
    specific = {name: affine_keys(pa, ca, a) for name, pa, ca, a in systems()}
    astra_tracks = committed("audit")["period_audit"]["tracks"]
    rows, disagreements = [], []
    for p in range(1, max_period + 1):
        residues = {i % p for i in CRIB_POSITIONS}
        ok_systems = []
        for name, keys in specific.items():
            seen = {}
            if all(seen.setdefault(i % p, k) == k for i, k in sorted(keys.items())):
                ok_systems.append(name)
        for name in specific:
            if (name in ok_systems) != (p in astra_tracks[name]["compatible_periods"]):
                disagreements.append({"period": p, "system": name})
        any_ok, any_bad = periodic_any_alphabets(p)
        latin_ok, latin_bad = periodic_latin_square(p)
        status, detail = graph.periodic(p, samples=q4_samples) if latin_ok else ("infeasible", {"via": "latin"})
        rows.append({
            "period": p, "fixed_tableau_checks": 24 - len(residues),
            "systems48_compatible": len(ok_systems), "systems48_names": ok_systems,
            "any_alphabets": any_ok,
            "any_alphabets_first_conflict_1b": [i + 1 for i in any_bad[0]] if any_bad else None,
            "latin_square": latin_ok,
            "latin_first_conflict_1b": [i + 1 for i in latin_bad[0]] if latin_bad else None,
            "keyed_vigenere_unknown_alphabets": status,
            "keyed_vigenere_detail": detail,
        })
    equal, unequal = crib_relations()
    return {
        "models": {
            "systems48": "Astra's 48 fixed ABC/KRYPTOS affine systems (recomputed independently)",
            "any_alphabets": "arbitrary unrelated alphabet per residue (weakest assumption)",
            "latin_square": "one unknown Latin-square tableau, rows chosen by residue key",
            "keyed_vigenere_unknown_alphabets": "c(C)=p(P)+k_r with unknown bijections p,c "
                                                "(Quagmire I-IV, KA tableau, Beaufort by relabelling)",
        },
        "equalities_1b": [[i + 1, j + 1] for i, j in equal],
        "inequalities_1b": [[i + 1, j + 1] for i, j in unequal],
        "disagreements_with_astra_48_system_audit": disagreements,
        "rows": rows,
        "summary": {
            "eliminated_for_any_alphabets_1to26": [r["period"] for r in rows if r["period"] <= 26 and not r["any_alphabets"]],
            "open_for_latin_square_1to26": [r["period"] for r in rows if r["period"] <= 26 and r["latin_square"]],
            "open_for_keyed_vigenere_1to26": [r["period"] for r in rows if r["period"] <= 26
                                              and r["keyed_vigenere_unknown_alphabets"] == "feasible"],
            "unresolved_keyed_vigenere": [r["period"] for r in rows
                                          if r["keyed_vigenere_unknown_alphabets"] == "open"],
        },
    }


# ---------------------------------------------------------- progressive key
def progressive_audit():
    tested, compatible, by_period = 0, 0, defaultdict(Counter)
    for name, pa, ca, a in systems():
        keys = affine_keys(pa, ca, a)
        for m in range(1, 27):
            for h in range(m):
                for d in range(26):
                    tested += 1
                    base = {}
                    ok = all(base.setdefault((i + h) % m, (k - d * ((i + h) // m)) % 26)
                             == (k - d * ((i + h) // m)) % 26 for i, k in sorted(keys.items()))
                    by_period[m]["tested"] += 1
                    if ok:
                        compatible += 1
                        by_period[m]["compatible"] += 1
    # Period 26 has exactly one repeated residue: positions 22 and 74 (1-based), 52 apart,
    # so compatibility is the single congruence 2d = K_74 - K_22 (mod 26).
    parity = []
    for name, pa, ca, a in systems():
        keys = affine_keys(pa, ca, a)
        delta = (keys[73] - keys[21]) % 26
        drifts = [d for d in range(26) if (2 * d - delta) % 26 == 0]
        parity.append({"system": name, "delta": delta, "delta_even": delta % 2 == 0,
                       "drifts": drifts, "same_alphabets": pa == ca})
    predicted = 26 * sum(len(r["drifts"]) for r in parity)
    astra = committed("progressive")
    return {
        "tested": tested, "compatible": compatible,
        "matches_astra": tested == astra["tested"] and compatible == astra["compatible"]
        and {int(k): v for k, v in astra["by_period"].items()} == {m: dict(c) for m, c in by_period.items()},
        "period26_rule": "compatible iff K_74 - K_22 is even; then d = delta/2 or delta/2 + 13",
        "period26_predicted_tuples": predicted, "period26_observed": by_period[26]["compatible"],
        "systems_with_even_delta": sum(r["delta_even"] for r in parity),
        "even_delta_systems_all_mixed_alphabets": all(not r["same_alphabets"] for r in parity if r["delta_even"]),
        "parity_rows": parity,
        "interpretation": "Survival at m=26 is a parity property of one equation, not a signal.",
    }


# ------------------------------------------------------- plaintext feedback
def feedback_audit():
    by_lag = defaultdict(Counter)
    for (pn, pa), (cn, ca) in product(ALPHABETS.items(), ALPHABETS.items()):
        cv = [ca.index(c) for c in K4]
        pv = {i: pa.index(p) for i, p in CRIBS.items()}
        for lag, a, b, t in product(range(1, 49), (1, 25), (1, 25), range(26)):
            inv = pow(a, -1, 26)
            ok = True
            for r in range(lag):
                chain = list(range(r, 97, lag))
                if not any(i in pv for i in chain):
                    continue
                viable = False
                for seed in ([pv[r]] if r in pv else range(26)):
                    value, good = seed, True
                    for i in chain[1:]:
                        value = (inv * (cv[i] - b * value - t)) % 26
                        if i in pv and pv[i] != value:
                            good = False
                            break
                    if good:
                        viable = True
                        break
                if not viable:
                    ok = False
                    break
            by_lag[lag]["tested"] += 1
            by_lag[lag]["compatible"] += ok
    astra = committed("feedback")
    checks = {lag: 24 - len({i % lag for i in CRIB_POSITIONS}) for lag in range(1, 49)}
    return {
        "matches_astra": all(astra["by_lag"][str(lag)].get(field, 0) == by_lag[lag][field]
                             for lag in range(1, 49) for field in ("tested", "compatible")),
        "compatible_by_lag": {lag: c["compatible"] for lag, c in by_lag.items() if c["compatible"]},
        "crib_repeat_checks_by_lag": checks,
        "interpretation": "Each residue chain modulo the lag is fixed by any crib in it; only "
                          "chains containing two cribs test anything. Lags 27-29 contain none, "
                          "lags 26 and 30 contain exactly one, so their survivors are expected.",
    }


# ------------------------------------------------------- affine recurrence
def _forward_ok(keys_mod, coeff, order, q):
    seq = [keys_mod[21 + j] for j in range(order)]
    for i in range(21 + order, 74):
        k = (coeff[-1] + sum(coeff[j] * seq[-1 - j] for j in range(order))) % q
        seq.append(k)
        if i in keys_mod and keys_mod[i] != k:
            return False
    return True


def recurrence_audit(brute13_max_order=4):
    """Split modulo 2 and 13 (CRT): survivors mod 26 = survivors mod 2 x survivors mod 13.

    Mod 2 is brute-forced for every order; mod 13 is brute-forced up to
    ``brute13_max_order`` and otherwise solved by an independent GF(13) elimination
    of the windowed equations followed by forward propagation of every solution.
    """
    rows, astra_rows = [], {(r["system"], r["order"]): r for r in committed("recurrence")["rows"]}
    disagreements = 0
    for name, pa, ca, a in systems():
        keys = affine_keys(pa, ca, a)
        for order in range(1, 9):
            counts = {}
            for q in (2, 13):
                km = {i: k % q for i, k in keys.items()}
                if q == 2 or order <= brute13_max_order:
                    counts[q] = sum(_forward_ok(km, c, order, q) for c in product(range(q), repeat=order + 1))
                else:
                    eqs = [i for i in km if all(i - j in km for j in range(1, order + 1))]
                    solved = solve_mod([[km[i - j] for j in range(1, order + 1)] + [1] for i in eqs],
                                       [km[i] for i in eqs], order + 1, q)
                    if solved is None:
                        counts[q] = 0
                    else:
                        base, basis = solved
                        counts[q] = 0
                        for t in product(range(q), repeat=len(basis)):
                            c = [(x + sum(s * v[n] for s, v in zip(t, basis))) % q for n, x in enumerate(base)]
                            counts[q] += _forward_ok(km, c, order, q)
            survivors = counts[2] * counts[13]
            disagreements += (survivors > 0) != bool(astra_rows[(name, order)]["survivors"])
            rows.append({"system": name, "order": order, "survivors_mod2": counts[2],
                         "survivors_mod13": counts[13], "survivors_mod26": survivors})
    return {"cases": len(rows), "eliminated": sum(r["survivors_mod26"] == 0 for r in rows),
            "disagreements_with_astra": disagreements,
            "cases_failing_mod2_only": sum(r["survivors_mod2"] == 0 < r["survivors_mod13"] for r in rows),
            "cases_failing_mod13_only": sum(r["survivors_mod13"] == 0 < r["survivors_mod2"] for r in rows),
            "rows": rows}


# ----------------------------------------------------------- running key
def sculpture_texts():
    """K1-K3 streams; K2 corrected (XLAYERTWO) and K3 plaintext rederived and checked."""
    from research.run_astra import source_texts
    texts = dict(source_texts())
    k1p = decrypt_affine(texts["K1_cipher"], [KA.index("PALIMPSEST"[i % 10]) for i in range(63)], KA, KA)
    assert k1p == texts["K1_plain"] == ("BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION")
    k2 = texts["K2_cipher"]
    fixes = []
    for at in range(len(k2) - 30, len(k2) + 1):
        for ch in ABC:
            trial = k2[:at] + ch + k2[at:]
            plain = decrypt_affine(trial, [KA.index("ABSCISSA"[i % 8]) for i in range(len(trial))], KA, KA)
            if plain.endswith("WESTXLAYERTWO") and plain[:at] == texts["K2_plain_as_inscribed"][:at]:
                fixes.append((at, ch, trial, plain))
    assert fixes, "no single-letter insertion reproduces XLAYERTWO"
    at, ch, k2c, k2p = fixes[0]
    k3c, k3p = texts["K3_cipher"], k3_decrypt(texts["K3_cipher"])
    return texts, {"K2_correction_insert_0b": at, "K2_correction_letter": ch,
                   "K2_correction_alternatives": len({f[2] for f in fixes}),
                   "K3_plain_head": k3p[:40], "K3_plain_tail": k3p[-30:]}, {
        "K2_cipher_corrected": k2c, "K2_plain_corrected": k2p, "K3_plain": k3p,
        "K1K2K3_plain_corrected": k1p + k2p + k3p, "K1K2K3_cipher_corrected": texts["K1_cipher"] + k2c + k3c}


def _rotate(rows, clockwise):
    h, w = len(rows), len(rows[0])
    if clockwise:
        return ["".join(rows[h - 1 - r][c] for r in range(h)) for c in range(w)]
    return ["".join(rows[r][w - 1 - c] for r in range(h)) for c in range(w)]


def k3_decrypt(cipher, check="SLOWLYDESPARATLYSLOWLYTHEREMAINS"):
    """Search grid-rotation pairs over divisor widths; return the unique English output."""
    n = len(cipher)
    widths = [w for w in range(2, n) if n % w == 0]
    found = set()
    for w1, cw1, w2, cw2 in product(widths, (True, False), widths, (True, False)):
        first = "".join(_rotate([cipher[i:i + w1] for i in range(0, n, w1)], cw1))
        second = "".join(_rotate([first[i:i + w2] for i in range(0, n, w2)], cw2))
        if second.startswith(check):
            found.add(second)
    assert len(found) == 1, f"expected one K3 decryption, found {len(found)}"
    return found.pop()


def running_key_audit():
    texts, provenance, extra = sculpture_texts()
    astra_names = ["K1_cipher", "K2_cipher", "K3_cipher", "K1_plain", "K2_plain_as_inscribed",
                   "K1K2K3_cipher", "K1K2_plain_as_inscribed"]
    req = {name: affine_keys(pa, ca, a) for name, pa, ca, a in systems()}
    result = {}
    for label, names, streams in (("astra_streams_recomputed", astra_names, texts),
                                  ("gap_fill_streams", list(extra), extra)):
        tested, best, hits = 0, Counter(), []
        for sname in names:
            src = streams[sname]
            for direction, (kn, kal) in product((1, -1), ALPHABETS.items()):
                vals = [kal.index(c) for c in src]
                L = len(src)
                for sysname, keys in req.items():
                    for off in range(L):
                        diffs = Counter((k - vals[(off + direction * i) % L]) % 26 for i, k in keys.items())
                        shift, top = diffs.most_common(1)[0]
                        tested += 26
                        best[top] += 1
                        if top == 24:
                            hits.append({"stream": sname, "direction": direction, "key_alphabet": kn,
                                         "system": sysname, "offset": off, "shift": shift})
        result[label] = {"streams": {n: len(streams[n]) for n in names},
                         "tested_tuples": tested, "full_24_hits": hits,
                         "best_partial": max(best), "partial_histogram": dict(sorted(best.items()))}
    astra = committed("running")
    result["matches_astra"] = (result["astra_streams_recomputed"]["tested_tuples"] == astra["tested_parameter_tuples"]
                               and not astra["full_anchor_hits"]
                               and not result["astra_streams_recomputed"]["full_24_hits"]
                               and result["astra_streams_recomputed"]["best_partial"]
                               == astra["top_10_partial_matches_not_candidates"][0]["anchor_matches"])
    result["provenance"] = provenance
    return result


# ---------------------------------------------------------- planted attacks
def planted_audit(trials=300, seed=20261007):
    """Plant solutions inside each 'eliminated' family and run Astra's own checkers.

    A sound elimination must never reject a planted member of its family.
    """
    from research.k4_core import (feedback_constraints, implied_keys, periodic_constraints,
                                  recurrence_candidates)
    rng = random.Random(seed)
    sys_list = list(systems())
    plain_pool = sculpture_texts()[2]["K1K2K3_plain_corrected"]
    failures = Counter()
    runs = Counter()

    def plaintext():
        start = rng.randrange(len(plain_pool) - 97)
        text = list(plain_pool[start:start + 97])
        for i, ch in CRIBS.items():
            text[i] = ch
        return "".join(text)

    for _ in range(trials):
        name, pa, ca, a = rng.choice(sys_list)
        plain = plaintext()
        # recurrence of random order, arbitrary (possibly non-invertible) coefficients
        order = rng.randrange(1, 9)
        coeff = [rng.randrange(26) for _ in range(order + 1)]
        seq = [rng.randrange(26) for _ in range(order)]
        while len(seq) < 97:
            seq.append((coeff[-1] + sum(coeff[j] * seq[-1 - j] for j in range(order))) % 26)
        cipher = encrypt_affine(plain, seq, pa, ca, a)
        res = recurrence_candidates(implied_keys(cipher, CRIBS, pa, ca, a), order)
        runs["recurrence"] += 1
        runs["recurrence_capped_left_open"] += not res["complete"]
        failures["recurrence"] += res["complete"] and coeff not in res["survivors"]
        # progressive key with random period/phase/drift
        m, d = rng.randrange(1, 27), rng.randrange(26)
        h = rng.randrange(m)
        base = [rng.randrange(26) for _ in range(m)]
        key = [(base[(i + h) % m] + d * ((i + h) // m)) % 26 for i in range(97)]
        cipher = encrypt_affine(plain, key, pa, ca, a)
        runs["progressive"] += 1
        failures["progressive"] += bool(periodic_constraints(implied_keys(cipher, CRIBS, pa, ca, a), m, h, d)[1])
        # plaintext feedback (autokey) with arbitrary primer ciphertext
        lag, fa, fb, t = rng.randrange(1, 49), rng.choice((1, 25)), rng.choice((1, 25)), rng.randrange(26)
        fpa, fca = rng.choice((ABC, KA)), rng.choice((ABC, KA))
        cipher = "".join(rng.choice(ABC) if i < lag else
                         fca[(fa * fpa.index(p) + fb * fpa.index(plain[i - lag]) + t) % 26]
                         for i, p in enumerate(plain))
        out = feedback_constraints(cipher, CRIBS, lag, fa, fb, t, fpa, fca)
        runs["feedback"] += 1
        failures["feedback"] += out is None or any(
            fpa.index(plain[r]) not in out["allowed_seed_values"][r] for r in range(lag))
    # running key: plant into a stream and rerun Astra's complete search on it
    import research.run_astra as astra
    from research import k4_core
    original = astra.implied_keys
    streams = astra.source_texts()
    for _ in range(4):
        sname = rng.choice(sorted(streams))
        src = streams[sname]
        direction, (kn, kal) = rng.choice((1, -1)), rng.choice(sorted(ALPHABETS.items()))
        name, pa, ca, a = rng.choice(sys_list)
        off, shift = rng.randrange(len(src)), rng.randrange(26)
        key = [(kal.index(src[(off + direction * i) % len(src)]) + shift) % 26 for i in range(97)]
        cipher = encrypt_affine(plaintext(), key, pa, ca, a)
        astra.implied_keys = lambda cipher_=cipher, **kw: k4_core.implied_keys(cipher_, **kw)
        try:
            found = astra.running_key_attack()["full_anchor_hits"]
        finally:
            astra.implied_keys = original
        runs["running"] += 1
        failures["running"] += not any(h["source"] == sname and h["offset"] == off and h["direction"] == direction
                                       and h["key_alphabet"] == kn and h["system"] == name for h in found)
    return {"seed": seed, "runs": dict(runs), "planted_rejections": dict(failures),
            "interpretation": "Zero rejections means no counterexample to soundness was found "
                              "for these families; it does not test the families' relevance."}


# ------------------------------------------------------------ identifiability
def identifiability(samples=200000, seed=1):
    """How many bits do the 24 cribs carry about a key schedule, by alphabet assumption?"""
    rng = random.Random(seed)
    graph = QuagmireGraph()
    # The conditional sampler below solves these two cycle conditions explicitly.
    assert graph.cycles == [{23: -1, 32: 1, 28: 1, 33: -1}, {27: 1, 65: -1}], graph.cycles
    equal, unequal = crib_relations()
    cond_ok = 0
    any_ok = latin_ok = 0
    for _ in range(samples):
        k = {i: rng.randrange(26) for i in CRIB_POSITIONS}
        a_ok = all(k[i] != k[j] for i, j in unequal)
        any_ok += a_ok
        latin_ok += a_ok and all(k[i] == k[j] for i, j in equal)
        # sample conditional on the two linear cycle conditions, which hold w.p. 1/26^2
        k[65] = k[27]
        k[33] = (k[28] - k[23] + k[32]) % 26
        cond_ok += graph.feasible(k)
    p_q4 = cond_ok / samples / 26 ** 2
    gromark = Fraction(39, 99999)
    return {
        "samples": samples,
        "fixed_known_tableau": {"fraction": "26^-24", "bits": round(24 * log2(26), 1)},
        "any_alphabets_per_key_value": {"fraction": any_ok / samples, "bits": round(-log2(any_ok / samples), 2)},
        "latin_square_tableau": {"fraction": latin_ok / samples, "bits": round(-log2(latin_ok / samples), 2)},
        "keyed_vigenere_unknown_alphabets": {
            "fraction": p_q4, "bits": round(-log2(p_q4), 2),
            "conditional_on_cycle_conditions": cond_ok / samples},
        "gromark_base10_primer5_reproduced_count": "39/99999",
        "gromark_bits": round(-log2(float(gromark)), 2),
        "interpretation": "With the tableau known, the cribs carry about 113 bits about the key "
                          "schedule; with keyed alphabets unknown, about 11; with an arbitrary "
                          "Latin square, about 6. Any schedule family larger than these budgets "
                          "will have crib-compatible members by chance.",
    }


def gromark_audit():
    """Reproduce Bean (2021) primer counts with the exact Quagmire-IV solver."""
    graph = QuagmireGraph()
    out = {}
    for base, length in ((10, 5), (8, 5), (10, 4)):
        found = []
        for primer in all_primers(base, length):
            if any(primer):
                key = lagged_fibonacci(primer, base, 74)
                if graph.feasible({i: key[i] for i in CRIB_POSITIONS}):
                    found.append("".join(map(str, primer)))
        out[f"base{base}_primer{length}"] = {"count": len(found), "primers": found}
    out["bean_2021_reported"] = {"base10_primer5": 39, "base8_primer5": "4, including 00351 and 00537",
                                 "base10_primer4": "3301, 6740, 9903 (printed as '33015, 6740, and 9903')"}
    out["agrees_with_bean"] = (out["base10_primer5"]["count"] == 39
                               and {"26717", "84393", "98800"} <= set(out["base10_primer5"]["primers"])
                               and out["base8_primer5"]["count"] == 4
                               and {"00351", "00537"} <= set(out["base8_primer5"]["primers"])
                               and out["base10_primer4"]["primers"] == ["3301", "6740", "9903"])
    return out


def transcription_shift_audit(deltas=(-3, -2, -1, 1, 2, 3)):
    """Exploratory, not pre-registered: one net omission/insertion between the crib blocks.

    K2 on the sculpture omits one letter (an S; see sculpture_texts). If K4 had such an
    error between positions 35 and 63, every absolute-position key would index
    BERLINCLOCK at sculpture position + delta. Test the strong families under that shift.
    """
    texts, _, extra = sculpture_texts()
    streams = {**{k: texts[k] for k in ("K1_cipher", "K2_cipher", "K3_cipher", "K1_plain",
                                        "K2_plain_as_inscribed", "K1K2K3_cipher", "K1K2_plain_as_inscribed")}, **extra}
    out = []
    for delta in deltas:
        cribs = {(i + delta if i >= 63 else i): ch for i, ch in CRIBS.items()}
        cipher_at = {(i + delta if i >= 63 else i): K4[i] for i in CRIBS}
        keyed = {name: {j: (ca.index(cipher_at[j]) - a * pa.index(p)) % 26 for j, p in cribs.items()}
                 for name, pa, ca, a in systems()}
        periodic = []
        for name, keys in keyed.items():
            for p in range(1, 27):
                seen = {}
                if all(seen.setdefault(j % p, k) == k for j, k in sorted(keys.items())):
                    periodic.append({"system": name, "period": p, "checks": 24 - len({j % p for j in keys})})
        positions = sorted(cribs)
        latin_open = [p for p in range(1, 27) if periodic_latin_square(
            p, cipher="".join(cipher_at.get(i, "A") for i in range(max(positions) + 1)), cribs=cribs)[0]]
        hits, best = 0, 0
        for src in streams.values():
            L = len(src)
            for direction, kal in product((1, -1), (ABC, KA)):
                vals = [kal.index(c) for c in src]
                for keys in keyed.values():
                    for off in range(L):
                        top = Counter((k - vals[(off + direction * j) % L]) % 26 for j, k in keys.items()).most_common(1)[0][1]
                        best = max(best, top)
                        hits += top == 24
        out.append({"delta": delta, "periodic48_compatible_period_le24": [r for r in periodic if r["period"] <= 24],
                    "periodic48_compatible_25_26_all_zero_or_one_check": all(r["checks"] <= 1 for r in periodic if r["period"] > 24),
                    "latin_square_open_periods_le26": latin_open,
                    "running_key_full_hits": hits, "running_key_best_partial": best})
    return {"scope": "Block 2 (BERLINCLOCK) key index = sculpture index + delta; block 1 unchanged. "
                     "48 fixed systems (periodic p<=26), Latin-square periodic, and all 12 sculpture "
                     "running-key streams with every offset, direction and key alphabet.",
            "status": "exploratory, not pre-registered", "rows": out}


def english_corpus():
    """Local English letters: Python's bundled reference text (technical prose)."""
    import pydoc_data.topics as topics
    import re
    return re.sub(r"[^A-Z]", "", " ".join(topics.topics[k] for k in sorted(topics.topics)).upper())


def trigram_model(text, k=0.5):
    tri, bi = Counter(text[i:i + 3] for i in range(len(text) - 2)), Counter(text[i:i + 2] for i in range(len(text) - 1))
    return lambda s: sum(log2((tri[s[i:i + 3]] + k) / (bi[s[i:i + 2]] + 26 * k)) for i in range(len(s) - 2)) / (len(s) - 2)


def english_running_key_audit(seed=3):
    """Heuristic class test: under a known tableau, a running key's crib fragments are key text.

    For ABC/KRYPTOS plaintext and ciphertext alphabets, three sign conventions and
    ABC or KRYPTOS key-letter indexing, the 13- and 11-letter key fragments at the
    crib blocks must look like English if the key is English text from any source.
    """
    corpus = english_corpus()
    half = len(corpus) // 2
    score = trigram_model(corpus[:half])
    held_out = corpus[half:]
    plain_k = sculpture_texts()[2]["K1K2K3_plain_corrected"]
    rng = random.Random(seed)
    ref = {n: sorted(score(held_out[s:s + n]) for s in (rng.randrange(len(held_out) - n) for _ in range(20000)))
           for n in (13, 11)}
    ref_k = {n: sorted(score(plain_k[s:s + n]) for s in range(len(plain_k) - n)) for n in (13, 11)}
    rand = {n: sorted(score("".join(rng.choice(ABC) for _ in range(n))) for _ in range(20000)) for n in (13, 11)}

    def pct(table, value):
        return round(100 * sum(v <= value for v in table) / len(table), 2)

    rows = []
    for (pn, pa), (cn, ca) in product(ALPHABETS.items(), ALPHABETS.items()):
        for sign, f in (("vigenere", lambda c, p: c - p), ("beaufort", lambda c, p: c + p), ("variant", lambda c, p: p - c)):
            for kn, kal in ALPHABETS.items():
                frags = ["".join(kal[f(ca.index(K4[i]), pa.index(CRIBS[i])) % 26] for i in block) for block in BLOCKS]
                rows.append({"P": pn, "C": cn, "sign": sign, "key_letters": kn, "fragments": frags,
                             "percentile_in_english_13_11": [pct(ref[13], score(frags[0])), pct(ref[11], score(frags[1]))],
                             "percentile_reversed_13_11": [pct(ref[13], score(frags[0][::-1])), pct(ref[11], score(frags[1][::-1]))],
                             "percentile_in_K1K3_plain_13_11": [pct(ref_k[13], score(frags[0])), pct(ref_k[11], score(frags[1]))],
                             "percentile_in_random_13_11": [pct(rand[13], score(frags[0])), pct(rand[11], score(frags[1]))]})
    # positive control: K3 plaintext encrypted with an English running key under KRYPTOS Vigenere
    key_text = held_out[1000:1097]
    control_plain = plain_k[400:497]
    control = encrypt_affine(control_plain, [KA.index(c) for c in key_text], KA, KA)
    frag = ["".join(KA[(KA.index(control[i]) - KA.index(control_plain[i])) % 26] for i in block) for block in BLOCKS]
    return {"model": "letter trigrams from the first half of Python's bundled reference text; "
                     "percentiles against 20,000 held-out windows and all K1-K3 plaintext windows",
            "rows": rows,
            "max_english_percentile_any_combo": max(max(r["percentile_in_english_13_11"]) for r in rows),
            "max_block1_percentile_any_combo_either_direction": max(
                max(r["percentile_in_english_13_11"][0], r["percentile_reversed_13_11"][0]) for r in rows),
            "max_joint_tail_probability_either_direction": max(
                max(r["percentile_in_english_13_11"][0] * r["percentile_in_english_13_11"][1],
                    r["percentile_reversed_13_11"][0] * r["percentile_reversed_13_11"][1]) / 1e4 for r in rows),
            "positive_control": {"fragments": frag,
                                 "percentile_in_english_13_11": [pct(ref[13], score(frag[0])), pct(ref[11], score(frag[1]))]},
            "status": "heuristic language test; eliminates English running keys only for these tableaux"}


def ic_period_audit(trials=20000, seed=5):
    """How unusual is K4's IC (7/194) for a period-p polyalphabetic cipher of English?"""
    import numpy as np
    corpus = english_corpus()
    freq = np.array([corpus.count(c) for c in ABC], float)
    freq /= freq.sum()
    rng = np.random.default_rng(seed)
    target = 7 / 194
    rows = {}
    for p in list(range(1, 27)) + [97]:
        plain = rng.choice(26, size=(trials, 97), p=freq)
        key = rng.integers(0, 26, size=(trials, p))
        cipher = (plain + key[:, np.arange(97) % p]) % 26
        counts = np.stack([np.bincount(row, minlength=26) for row in cipher])
        ic = (counts * (counts - 1)).sum(axis=1) / (97 * 96)
        rows[p] = {"mean_ic": round(float(ic.mean()), 5), "p_ic_le_k4": round(float((ic <= target + 1e-12).mean()), 4)}
    return {"k4_ic": round(target, 5), "model": "i.i.d. letters with corpus frequencies; random shifts per residue; "
            "97 = no repetition", "by_period": rows,
            "status": "weak evidence only; real text is burstier than i.i.d. letters"}


def width_bigram_audit(permutations=100000, widths=range(1, 49), seed=11):
    """Exploratory: Bean's width-21 repeated vertical bigrams, corrected for scanning widths.

    Repeats at width w = (number of pairs (C_i, C_(i+w))) - (number of distinct pairs).
    The per-width p-value and the minimum over all scanned widths are both calibrated
    against random permutations of the K4 letters.
    """
    import numpy as np
    rng = np.random.default_rng(seed)
    base = np.array([ord(c) - 65 for c in K4], dtype=np.int16)
    widths = list(widths)

    def repeats(rows):
        out = np.empty((rows.shape[0], len(widths)), dtype=np.int16)
        for n, w in enumerate(widths):
            codes = np.sort(rows[:, :-w] * 26 + rows[:, w:], axis=1)
            out[:, n] = (codes[:, 1:] == codes[:, :-1]).sum(axis=1)
        return out

    observed = repeats(base[None, :])[0]
    null = np.concatenate([repeats(np.stack([rng.permutation(base) for _ in range(10000)]))
                           for _ in range(permutations // 10000)])
    tail = (null >= observed).mean(axis=0)                     # per-width p-values for K4
    ranks = np.argsort(np.argsort(-null, axis=0, kind="stable"), axis=0)
    null_p = (ranks + 1) / len(null)                           # per-width p-values of null rows
    min_null = null_p.min(axis=1)
    k4_min = tail.min()
    return {"widths": widths, "observed_repeats": observed.tolist(),
            "per_width_p": [round(float(x), 6) for x in tail],
            "width21": {"repeats": int(observed[widths.index(21)]), "p": float(tail[widths.index(21)])},
            "most_extreme_width": widths[int(tail.argmin())], "min_p": float(k4_min),
            "scan_corrected_p": float((min_null <= k4_min).mean()), "permutations": len(null),
            "status": "exploratory; Bean (2021) reported 11 repeats at width 21, about 1 in 6,750"}


def p27_audit():
    """Recompute the period-27 template and its forced text without Astra's code."""
    keys = affine_keys()
    cycle = {}
    for i, k in keys.items():
        assert cycle.setdefault(i % 27, k) == k
    forced = "".join(ABC[(ABC.index(c) - cycle[i % 27]) % 26] if i % 27 in cycle else "?"
                     for i, c in enumerate(K4))
    return {"template": "".join(ABC[cycle[r]] if r in cycle else "?" for r in range(27)),
            "unknown_residues_0b": sorted(set(range(27)) - set(cycle)),
            "forced_text": forced, "forced_count": 97 - forced.count("?"),
            "matches_handoff": forced == ("QDEPKOY??VANRHIBUOOB?EASTNORTHEAST??KZSIYKIENXZ?VPUHHJWFCY"
                                          "MIO??BERLINCLOCK?FSLXURLEXGWKV??OAGARUH")}


def legacy_exports_audit():
    """Independent replay of the historical exports' plaintext/key rows."""
    import csv
    out = {}
    for name in ("k4_top10_summary.json", "k4_top100_candidates_light.csv",
                 "kryptos_k4_top50_period27.csv", "kryptos_k4_top100_period27_quadgram_composite.csv"):
        path = ROOT / name
        rows = json.loads(path.read_text()) if name.endswith(".json") else list(csv.DictReader(path.open()))
        phases = Counter()
        for row in rows:
            row = {k.lower(): v for k, v in row.items()}
            key, plain = row["keystream_27"], row["plaintext"]
            match = [h for h in range(27) if decrypt_affine(K4, [ABC.index(key[(i + h) % 27]) for i in range(97)]) == plain]
            phases[tuple(match)] += 1
        out[name] = {"rows": len(rows), "matching_phases": {str(list(k)): v for k, v in phases.items()}}
    return out

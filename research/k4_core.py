"""Exact, dependency-free K4 arithmetic; all positions in code are zero based."""
from __future__ import annotations

from itertools import product
from math import gcd

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CIPHER = (
    "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYP"
    "VTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
)
ISLANDS = ((22, "EAST"), (26, "NORTHEAST"), (64, "BERLIN"), (70, "CLOCK"))
CRIBS = {start - 1 + j: c for start, word in ISLANDS for j, c in enumerate(word)}
UNITS = tuple(a for a in range(26) if gcd(a, 26) == 1)
ALPHABETS = {"ABC": ABC, "KRYPTOS": KA}


def systems():
    """C_numeric = a * P_numeric + K, for four alphabet pairs and 12 units."""
    for pn, cn, a in product(ALPHABETS, ALPHABETS, UNITS):
        yield f"P={pn};C={cn};a={a}", ALPHABETS[pn], ALPHABETS[cn], a


def implied_keys(cipher=CIPHER, cribs=CRIBS, pa=ABC, ca=ABC, a=1):
    return {i: (ca.index(cipher[i]) - a * pa.index(p)) % 26 for i, p in cribs.items()}


def decrypt(cipher, key, pa=ABC, ca=ABC, a=1):
    assert len(cipher) == len(key)
    inv = pow(a, -1, 26)
    return "".join(pa[((ca.index(c) - k) * inv) % 26] for c, k in zip(cipher, key))


def encrypt(plain, key, pa=ABC, ca=ABC, a=1):
    assert len(plain) == len(key)
    return "".join(ca[(a * pa.index(p) + k) % 26] for p, k in zip(plain, key))


def candidate_check(plain, regenerated_cipher, cipher=CIPHER, cribs=CRIBS):
    """Consistency only: passing is necessary, never sufficient for a solution."""
    exact_length = len(plain) == len(cipher) == 97
    anchors = sum(i < len(plain) and plain[i] == p for i, p in cribs.items())
    matches = sum(x == y for x, y in zip(regenerated_cipher, cipher))
    return {
        "plaintext_length": len(plain),
        "anchor_matches": anchors,
        "ciphertext_matches": matches,
        "consistent": exact_length and anchors == len(cribs)
        and regenerated_cipher == cipher,
        "is_solution": False,
        "note": "A fitted key and a round trip do not independently establish a solution.",
    }


def periodic_constraints(keys, period, phase=0, drift=0):
    """K_i = B_((i+phase) mod period) + drift*floor((i+phase)/period)."""
    values, first, conflicts = {}, {}, []
    for i, k in sorted(keys.items()):
        r, q = (i + phase) % period, (i + phase) // period
        b = (k - drift * q) % 26
        if r in values and values[r] != b:
            conflicts.append({"positions_1b": [first[r] + 1, i + 1],
                              "required_values": [values[r], b], "residue_0b": r})
        else:
            values[r] = b
            first.setdefault(r, i)
    return values, conflicts


def linear_solutions(rows, rhs, nvars, prime):
    """RREF over GF(prime), returning one solution and a nullspace basis, or None."""
    matrix = [[v % prime for v in row] + [b % prime] for row, b in zip(rows, rhs)]
    pivots, rank = [], 0
    for col in range(nvars):
        pivot = next((r for r in range(rank, len(matrix)) if matrix[r][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inv = pow(matrix[rank][col], -1, prime)
        matrix[rank] = [(v * inv) % prime for v in matrix[rank]]
        for r in range(len(matrix)):
            if r != rank and matrix[r][col]:
                f = matrix[r][col]
                matrix[r] = [(x - f * y) % prime for x, y in zip(matrix[r], matrix[rank])]
        pivots.append(col)
        rank += 1
    if any(not any(row[:nvars]) and row[-1] for row in matrix):
        return None
    base = [0] * nvars
    for r, col in enumerate(pivots):
        base[col] = matrix[r][-1]
    basis = []
    for free in sorted(set(range(nvars)) - set(pivots)):
        vector = [0] * nvars
        vector[free] = 1
        for r, col in enumerate(pivots):
            vector[col] = -matrix[r][free] % prime
        basis.append(vector)
    return base, basis


def enumerate_field(solution, prime):
    base, basis = solution
    for coefficients in product(range(prime), repeat=len(basis)):
        yield [(x + sum(c * v[i] for c, v in zip(coefficients, basis))) % prime
               for i, x in enumerate(base)]


def recurrence_candidates(keys, order, cap=100000):
    """Exhaust affine recurrences modulo 26 by CRT; fail open if a cap is reached.

    K_i = c + sum(coeff[j-1] * K_(i-j), j=1..order).
    Local equations use only wholly observed windows. All resulting coefficients
    are then checked by forward propagation between both crib blocks. A failure
    after position 22 eliminates the model whatever its unknown initial seed.
    """
    positions = [i for i in keys if all(i - j in keys for j in range(1, order + 1))]
    rows = [[keys[i - j] for j in range(1, order + 1)] + [1] for i in positions]
    rhs = [keys[i] for i in positions]
    solutions = [linear_solutions(rows, rhs, order + 1, p) for p in (2, 13)]
    result = {"order": order, "local_equations": len(rows), "coefficient_vectors": 0,
              "forward_checked": 0, "survivors": [], "complete": True}
    if None in solutions:
        result["rejection_stage"] = "local_equations"
        return result
    count = 2 ** len(solutions[0][1]) * 13 ** len(solutions[1][1])
    result["coefficient_vectors"] = count
    if count > cap:
        result.update(complete=False, rejection_stage="enumeration_cap")
        return result
    start = next(i for i in sorted(keys) if all(i + j in keys for j in range(order)))
    vectors13 = list(enumerate_field(solutions[1], 13))
    for x2 in enumerate_field(solutions[0], 2):
        for x13 in vectors13:
            coeff = [(13 * u + 14 * v) % 26 for u, v in zip(x2, x13)]
            seq = [keys[start + j] for j in range(order)]
            result["forward_checked"] += 1
            for i in range(start + order, max(keys) + 1):
                k = (coeff[-1] + sum(coeff[j - 1] * seq[-j]
                                     for j in range(1, order + 1))) % 26
                seq.append(k)
                if i in keys and keys[i] != k:
                    break
            else:
                result["survivors"].append(coeff)
    result["rejection_stage"] = "forward_between_cribs" if not result["survivors"] else None
    return result


def feedback_constraints(cipher, cribs, lag, a=1, b=1, shift=0, pa=ABC, ca=ABC):
    """C_i = a P_i + b P_(i-lag) + shift after a free lag-letter primer.

    Each residue chain starts from one unknown P_r. Enumerating its 26 values is
    exact, including noninvertible b. Return allowable starts and a consistency
    witness. No language score enters the test.
    """
    inv = pow(a, -1, 26)
    cv = [ca.index(c) for c in cipher]
    pv = {i: pa.index(p) for i, p in cribs.items()}
    allowed, templates = [], []
    for r in range(lag):
        viable = []
        for first in range(26):
            value, chain = first, [first]
            if r in pv and value != pv[r]:
                continue
            for i in range(r + lag, len(cipher), lag):
                value = (inv * (cv[i] - b * value - shift)) % 26
                chain.append(value)
                if i in pv and value != pv[i]:
                    break
            else:
                viable.append((first, chain))
        if not viable:
            return None
        allowed.append([f for f, _ in viable])
        templates.append(viable)
    plain = ["?"] * len(cipher)
    for r, chains in enumerate(templates):
        for j in range(len(chains[0][1])):
            letters = {pa[chain[j]] for _, chain in chains}
            if len(letters) == 1:
                plain[r + j * lag] = letters.pop()
    return {"allowed_seed_values": allowed, "forced_plaintext": "".join(plain)}

"""Independent K4 primitives for the Opus review; all positions are zero based.

Deliberately written without importing ``research.k4_core`` so that agreement
between the two implementations is evidence rather than repetition.
"""
from __future__ import annotations

from collections import deque
import hashlib
from itertools import combinations, product
from math import gcd
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4_SHA256 = "eea813570c7f1fd3b34674e47b5c3da8948026f5cefee612a0b38ffaa515ceab"
K4 = (ROOT / "K4_ciphertext.txt").read_text().strip()
assert len(K4) == 97 and hashlib.sha256(K4.encode()).hexdigest() == K4_SHA256
ANCHORS_1B = ((22, "EAST"), (26, "NORTHEAST"), (64, "BERLIN"), (70, "CLOCK"))
CRIBS = {start - 1 + j: ch for start, word in ANCHORS_1B for j, ch in enumerate(word)}
CRIB_POSITIONS = tuple(sorted(CRIBS))
BLOCKS = (tuple(range(21, 34)), tuple(range(63, 74)))
UNITS = tuple(a for a in range(26) if gcd(a, 26) == 1)


# --------------------------------------------------------------------------- alphabets
def keyword_alphabet(word, mode="kryptos"):
    """Keyword-mixed alphabet.

    kryptos:  deduplicated keyword, then unused letters A..Z (KRYPTOS gives KA)
    continue: deduplicated keyword, then unused letters from the one after its last letter
    columnar: the kryptos-mode alphabet written in rows under the deduplicated keyword,
              read down the columns in alphabetical order of the keyword letters
    """
    seen = []
    for ch in word.upper():
        if ch in ABC and ch not in seen:
            seen.append(ch)
    if mode == "kryptos":
        return "".join(seen + [c for c in ABC if c not in seen])
    if mode == "continue":
        start = ABC.index(seen[-1]) + 1 if seen else 0
        return "".join(seen + [c for c in (ABC[start:] + ABC[:start]) if c not in seen])
    if mode == "columnar":
        base, width = keyword_alphabet(word, "kryptos"), max(1, len(seen))
        rows = [base[i:i + width] for i in range(0, 26, width)]
        order = sorted(range(width), key=lambda j: base[j])
        return "".join(row[j] for j in order for row in rows if j < len(row))
    raise ValueError(mode)


def affine_keys(pa=ABC, ca=ABC, a=1, cipher=K4, cribs=CRIBS):
    """Key values for C_num = a*P_num + K (mod 26): Vigenere a=1, Beaufort a=25."""
    return {i: (ca.index(cipher[i]) - a * pa.index(p)) % 26 for i, p in cribs.items()}


def encrypt_affine(plain, key, pa=ABC, ca=ABC, a=1):
    return "".join(ca[(a * pa.index(p) + k) % 26] for p, k in zip(plain, key))


def decrypt_affine(cipher, key, pa=ABC, ca=ABC, a=1):
    inv = pow(a, -1, 26)
    return "".join(pa[((ca.index(c) - k) * inv) % 26] for c, k in zip(cipher, key))


# ------------------------------------------------------------ alphabet-free relations
def crib_relations(cipher=K4, cribs=CRIBS):
    """Consequences of 'position i is enciphered by a bijection chosen by key value k_i'.

    Same plaintext with different ciphertext, or the reverse, forces k_i != k_j for
    every keyed substitution. An identical (plaintext, ciphertext) pair forces
    k_i == k_j whenever distinct keys move every letter differently, which holds for
    any Latin-square tableau, including all keyed Vigenere/Beaufort/Quagmire tables.
    """
    equal, unequal = [], []
    for i, j in combinations(sorted(cribs), 2):
        same_p, same_c = cribs[i] == cribs[j], cipher[i] == cipher[j]
        if same_p and same_c:
            equal.append((i, j))
        elif same_p or same_c:
            unequal.append((i, j))
    return equal, unequal


def periodic_any_alphabets(period, cipher=K4, cribs=CRIBS):
    """Period-p substitution with an arbitrary, unrelated alphabet for each residue."""
    _, unequal = crib_relations(cipher, cribs)
    bad = [(i, j) for i, j in unequal if i % period == j % period]
    return not bad, bad


def periodic_latin_square(period, cipher=K4, cribs=CRIBS):
    """Period-p substitution using rows of one unknown Latin-square tableau.

    Identical pairs merge residues onto one row; a merged group may not contain an
    inequality pair. At most 24 cells are filled, fewer than the order 26, so every
    consistent partial square completes (Evans' conjecture, proved by Smetaniuk 1981).
    """
    equal, unequal = crib_relations(cipher, cribs)
    parent = list(range(period))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, j in equal:
        parent[find(i % period)] = find(j % period)
    bad = [(i, j) for i, j in unequal if find(i % period) == find(j % period)]
    return not bad, bad


# ------------------------------------------------------------- modular linear algebra
def solve_mod(rows, rhs, nvars, q):
    """Solve rows.x = rhs over GF(q), q prime: (particular, nullspace basis) or None."""
    m = [[v % q for v in row] + [b % q] for row, b in zip(rows, rhs)]
    pivots, r = [], 0
    for col in range(nvars):
        piv = next((i for i in range(r, len(m)) if m[i][col]), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        inv = pow(m[r][col], -1, q)
        m[r] = [(v * inv) % q for v in m[r]]
        for i in range(len(m)):
            if i != r and m[i][col]:
                f = m[i][col]
                m[i] = [(x - f * y) % q for x, y in zip(m[i], m[r])]
        pivots.append(col)
        r += 1
    if any(row[-1] and not any(row[:-1]) for row in m):
        return None
    particular = [0] * nvars
    for i, col in enumerate(pivots):
        particular[col] = m[i][-1]
    basis = []
    for free in (c for c in range(nvars) if c not in pivots):
        vec = [0] * nvars
        vec[free] = 1
        for i, col in enumerate(pivots):
            vec[col] = (-m[i][free]) % q
        basis.append(vec)
    return particular, basis


def crt26(x2, x13):
    """Combine residues modulo 2 and 13 into residues modulo 26."""
    return [(13 * a + 14 * b) % 26 for a, b in zip(x2, x13)]


def combine(a, b, scale=1):
    """Integer linear forms as {crib position: coefficient}; returns a + scale*b."""
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0) + scale * v
    return {k: v for k, v in out.items() if v}


# ----------------------------------------------------- Quagmire-IV feasibility solver
class QuagmireGraph:
    """Exact feasibility of c(C_i) = p(P_i) + k_i (mod 26) for unknown bijections p, c.

    Vigenere, variant Beaufort and Beaufort with arbitrary mixed alphabets, Quagmire
    I-IV, the KRYPTOS tableau and Gromark-style numeric keys are all instances: the
    sign conventions are absorbed by relabelling p -> -p or c -> -c.

    The crib letters form a bipartite graph (plaintext letters, ciphertext letters;
    one edge per crib position). Along a spanning forest every letter's value is
    the component root plus a signed sum of key values. Each non-tree edge yields a
    linear condition on keys, letters in one component must receive distinct values,
    and components must then be packed into Z/26 by independent shifts.
    """

    def __init__(self, cipher=K4, cribs=CRIBS):
        self.cipher, self.cribs = cipher, dict(cribs)
        adjacency = {}
        for i in sorted(cribs):
            u, v = ("P", cribs[i]), ("C", cipher[i])
            adjacency.setdefault(u, []).append((v, i, 1))
            adjacency.setdefault(v, []).append((u, i, -1))
        self.form, self.components, self.cycles = {}, [], []
        tree = set()
        for root in sorted(adjacency):
            if root in self.form:
                continue
            self.form[root] = {}
            members, queue = [root], deque([root])
            while queue:
                node = queue.popleft()
                for other, i, sign in adjacency[node]:
                    if other not in self.form:
                        self.form[other] = combine(self.form[node], {i: sign})
                        tree.add(i)
                        members.append(other)
                        queue.append(other)
            self.components.append(members)
        for i in sorted(cribs):
            if i in tree:
                continue
            u, v = ("P", cribs[i]), ("C", cipher[i])
            self.cycles.append(combine(combine(self.form[v], self.form[u], -1), {i: 1}, -1))
        self.distinct = []
        for members in self.components:
            for kind in "PC":
                nodes = [n for n in members if n[0] == kind]
                for a, b in combinations(nodes, 2):
                    self.distinct.append(((a, b), combine(self.form[a], self.form[b], -1)))

    @staticmethod
    def evaluate(form, keys):
        return sum(c * keys[i] for i, c in form.items()) % 26

    def pack(self, rel):
        """Shift whole components so that all p values and all c values are distinct."""
        comps = sorted(self.components, key=len, reverse=True)
        shifts = [None] * len(comps)
        used = {"P": set(), "C": set()}

        def place(n):
            if n == len(comps):
                return True
            for s in range(26) if n else (0,):
                vals = {"P": [], "C": []}
                for node in comps[n]:
                    vals[node[0]].append((rel[node] + s) % 26)
                if any(len(set(v)) != len(v) or used[k] & set(v) for k, v in vals.items()):
                    continue
                for k in "PC":
                    used[k].update(vals[k])
                shifts[n] = s
                if place(n + 1):
                    return True
                for k in "PC":
                    used[k].difference_update(vals[k])
            return False

        if not place(0):
            return None
        return {node: (rel[node] + shifts[n]) % 26 for n, comp in enumerate(comps) for node in comp}

    def witness(self, keys):
        """Return explicit plaintext and ciphertext alphabets, or the first obstruction."""
        for cyc in self.cycles:
            if self.evaluate(cyc, keys):
                return None, {"obstruction": "cycle", "form_1b": {i + 1: c for i, c in cyc.items()}}
        for pair, diff in self.distinct:
            if not self.evaluate(diff, keys):
                return None, {"obstruction": "collision", "letters": pair}
        rel = {node: self.evaluate(form, keys) for node, form in self.form.items()}
        values = self.pack(rel)
        if values is None:
            return None, {"obstruction": "packing"}
        alphabets = {}
        for kind in "PC":
            slots = [None] * 26
            for (k, letter), v in values.items():
                if k == kind:
                    slots[v] = letter
            spare = iter(c for c in ABC if c not in slots)
            alphabets[kind] = "".join(c if c else next(spare) for c in slots)
        pa, ca = alphabets["P"], alphabets["C"]
        assert all(ca[(pa.index(self.cribs[i]) + keys[i]) % 26] == self.cipher[i] for i in self.cribs)
        return {"plain_alphabet": pa, "cipher_alphabet": ca}, None

    def feasible(self, keys):
        return self.witness(keys)[0] is not None

    # ---------------------------------------------------- key values as unknowns
    def periodic(self, period, samples=4000, seed=0):
        """Exact-or-witnessed feasibility for k_i = x_(i mod period), x unknown.

        Returns ("feasible", witness) from an explicit verified construction,
        ("infeasible", reason) from an algebraic proof, or ("open", note) if neither
        was obtained within the sampling budget.
        """
        residues = sorted({i % period for i in self.cribs})
        index = {r: n for n, r in enumerate(residues)}

        def lift(form):
            row = [0] * len(residues)
            for i, c in form.items():
                row[index[i % period]] += c
            return row

        rows = [lift(c) for c in self.cycles]
        kernels = {}
        for q in (2, 13):
            solved = solve_mod(rows, [0] * len(rows), len(residues), q)
            kernels[q] = solved[1]
        for pair, diff in self.distinct:
            f = lift(diff)
            if all(sum(a * b for a, b in zip(f, v)) % q == 0 for q in (2, 13) for v in kernels[q]):
                return "infeasible", {"forced_equal_letters": pair, "period": period}
        rng = random.Random(seed * 7919 + period)
        for _ in range(samples):
            parts = []
            for q in (2, 13):
                x = [0] * len(residues)
                for v in kernels[q]:
                    t = rng.randrange(q)
                    x = [(a + t * b) % q for a, b in zip(x, v)]
                parts.append(x)
            x = crt26(*parts)
            keys = {i: x[index[i % period]] for i in self.cribs}
            found, _ = self.witness(keys)
            if found:
                found["residue_keys"] = {r: x[index[r]] for r in residues}
                return "feasible", found
        return "open", {"samples": samples}


# ------------------------------------------------------------------ key generators
def lagged_fibonacci(primer, base, length=97):
    """Gromark-style expansion: k_i = k_(i-L) + k_(i-L+1) (mod base), L = len(primer)."""
    assert len(primer) >= 2
    key, lag = list(primer), len(primer)
    while len(key) < length:
        key.append((key[-lag] + key[-lag + 1]) % base)
    return key[:length]


def all_primers(base, length):
    return product(range(base), repeat=length)

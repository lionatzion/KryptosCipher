"""Explicit classical conventions, punctuation handling and reversible routes."""
from itertools import permutations

from .constants import FIXTURES, STD, KRYPTOS, K1_CIPHERTEXT, K2_CIPHERTEXT, K3_CIPHERTEXT

MODES = ("vigenere", "beaufort", "variant_beaufort")


def validate_alphabet(alphabet):
    if len(alphabet) != 26 or set(alphabet) != set(STD):
        raise ValueError("Alphabet must be a permutation of A through Z")


def implied_shift(plain, cipher, mode="vigenere"):
    if mode == "vigenere":
        return (cipher - plain) % 26
    if mode == "beaufort":
        return (cipher + plain) % 26
    if mode == "variant_beaufort":
        return (plain - cipher) % 26
    raise ValueError("Unknown substitution mode")


def transform(text, key, alphabet=STD, mode="vigenere", decrypt=False):
    """Numeric repeated key; pass through punctuation without advancing the key."""
    validate_alphabet(alphabet)
    key = tuple(key)
    if not key or any(type(k) is not int or not 0 <= k < 26 for k in key):
        raise ValueError("Key must contain integers in 0..25")
    if mode not in MODES:
        raise ValueError("Unknown substitution mode")
    out, j = [], 0
    for ch in text:
        if ch not in alphabet:
            out.append(ch)
            continue
        x, k = alphabet.index(ch), key[j % len(key)]
        if mode == "beaufort":
            y = k - x
        elif mode == "vigenere":
            y = x - k if decrypt else x + k
        else:
            y = x + k if decrypt else x - k
        out.append(alphabet[y % 26])
        j += 1
    return "".join(out)


def keyword_values(word, alphabet=KRYPTOS):
    validate_alphabet(alphabet)
    if not word or any(c not in alphabet for c in word):
        raise ValueError("Key word must be nonempty uppercase ASCII letters")
    return tuple(alphabet.index(c) for c in word)


def rotate(text, columns, clockwise=False):
    if columns < 1 or not text or len(text) % columns:
        raise ValueError("Rotation requires a nonempty complete rectangle")
    rows = len(text) // columns
    cs = range(columns) if clockwise else range(columns - 1, -1, -1)
    rs = range(rows - 1, -1, -1) if clockwise else range(rows)
    return "".join(text[r * columns + c] for c in cs for r in rs)


def corrected_k2():
    if K2_CIPHERTEXT[358:364] != "NUPLGE":
        raise ValueError("Unexpected K2 fixture, refusing positional correction")
    return K2_CIPHERTEXT[:364] + "S" + K2_CIPHERTEXT[364:]


def decode_k1():
    return transform(K1_CIPHERTEXT, keyword_values("PALIMPSEST"), KRYPTOS, decrypt=True)


def decode_k2(fix_sanborn_omitted_s=False):
    text = corrected_k2() if fix_sanborn_omitted_s else K2_CIPHERTEXT
    return transform(text, keyword_values("ABSCISSA"), KRYPTOS, decrypt=True)


def decode_k3():
    return rotate(rotate(K3_CIPHERTEXT[:-1], 24), 8) + "?"


def encode_k3(plaintext):
    if len(plaintext) != 337 or not plaintext.endswith("?"):
        raise ValueError("Expected 336 letters and the final physical question mark")
    return rotate(rotate(plaintext[:-1], 42, True), 14, True) + "?"


def verify_baselines():
    """Compare independent expected plaintexts AND exact ciphertext round trips."""
    compact = lambda text: text.replace(" ", "")
    k1 = compact(FIXTURES["K1_PLAINTEXT"])
    k2 = compact(FIXTURES["K2_PLAINTEXT"])
    k2_carved = k2[:-9] + "IDBYROWS"
    k3 = compact(FIXTURES["K3_PLAINTEXT"])
    return {
        "K1": decode_k1() == k1 and transform(k1, keyword_values("PALIMPSEST"), KRYPTOS) == K1_CIPHERTEXT,
        "K2_carved": decode_k2() == k2_carved and transform(k2_carved, keyword_values("ABSCISSA"), KRYPTOS) == K2_CIPHERTEXT,
        "K2_corrected": decode_k2(True) == k2 and transform(k2, keyword_values("ABSCISSA"), KRYPTOS) == corrected_k2(),
        "K3": decode_k3() == k3 and encode_k3(k3) == K3_CIPHERTEXT,
    }


def validate_permutation(permutation, length):
    if len(permutation) != length or sorted(permutation) != list(range(length)):
        raise ValueError("Gather route must be an exact permutation of positions")


def inverse_permutation(permutation):
    validate_permutation(permutation, len(permutation))
    inverse = [0] * len(permutation)
    for j, i in enumerate(permutation):
        inverse[i] = j
    return tuple(inverse)


def transpose(text, permutation):
    validate_permutation(permutation, len(text))
    return "".join(text[i] for i in permutation)


def remove_positions(text, null_positions):
    """Remove indexed cells, never every occurrence of a putative null letter."""
    indices = tuple(null_positions)
    if len(set(indices)) != len(indices) or any(type(i) is not int or not 0 <= i < len(text) for i in indices):
        raise ValueError("Null positions must be unique valid integer indices")
    removed = set(indices)
    return "".join(c for i, c in enumerate(text) if i not in removed)


def route_catalog(length=97, max_column_width=3, include_grids=True):
    """Deduplicated incomplete columnar and near-rectangular gather routes.

    Rectangular routes skip trailing unfilled cells. They do not insert letters.
    All inverses are included. This is a small, stated catalog, not all grids.
    """
    if length < 1 or not 1 <= max_column_width <= min(7, length):
        raise ValueError("Column width must be 1..min(7, length)")
    seen = set()
    def add(name, permutation):
        p = tuple(permutation)
        validate_permutation(p, length)
        for label, q in ((name, p), (name + ":inverse", inverse_permutation(p))):
            if q not in seen:
                seen.add(q)
                yield label, q
    yield from add("identity", range(length))
    for width in range(2, max_column_width + 1):
        for order in permutations(range(width)):
            yield from add("columnar:" + ",".join(map(str, order)),
                           [i for c in order for i in range(c, length, width)])
    if include_grids and length == 97:
        for rows, cols in ((7, 14), (14, 7), (8, 13), (13, 8), (5, 20), (10, 10), (11, 9)):
            for reverse_cols in (False, True):
                for snake in (False, True):
                    cs = list(range(cols))[::(-1 if reverse_cols else 1)]
                    p = [r * cols + c for j, c in enumerate(cs)
                         for r in (range(rows - 1, -1, -1) if snake and j % 2 else range(rows))
                         if r * cols + c < length]
                    yield from add(f"grid:{rows}x{cols}:reverse={reverse_cols}:snake={snake}", p)

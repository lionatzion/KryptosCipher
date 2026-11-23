"""
kryptos_analysis.py
====================

This module provides a collection of functions and data for working with
the codes from Jim Sanborn's **Kryptos** sculpture.  The first three
messages on the sculpture have been solved; they use classic cipher
techniques such as keyed Vigenère and double columnar transposition.
The fourth message remains unsolved and has inspired numerous
experiments – including AI‑assisted searches.  In addition to
decryption routines for the known messages, this module includes
experiments showing how one might apply gradient‑based optimisation to
simple substitution ciphers.  **It does not solve K4** but gives an
idea of how machine learning techniques could be used to explore
cipher space.

Usage examples are provided in the ``if __name__ == "__main__"`` block
at the bottom of the file.

The functions in this file are intended for educational use only.

References:
* James Sanborn's sculpture Kryptos: the left side of the screen contains
  four ciphers K1–K4.  The ciphertext lines used here are taken
  directly from the sculpture and replicated in the CIA and
  Wikipedia descriptions【684399955550168†L230-L270】.
* The solved plaintexts and the encryption methods are documented on
  Rumkin.com【450144964858183†L31-L46】 and other cryptographic
  analyses【228526962033129†L11-L41】.

The gradient‑descent example is inspired by general optimisation
techniques and does not correspond to any known solution of the
Kryptos K4 cipher.
"""

from __future__ import annotations
import itertools
import math
import random
from collections import Counter
from typing import Dict, Iterable, List, Tuple

################################################################################
# Data: ciphertext and plaintext sections
################################################################################

# Raw ciphertext as it appears on the left side of the Kryptos sculpture.  The
# four sections K1–K4 are separated here for convenience.  Lines come from
# the Wikipedia listing of the sculpture's 869‑character ciphertext【684399955550168†L230-L270】.

K1_CIPHERTEXT = (
    "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJ"
    "YQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
)

K2_CIPHERTEXT = (
    "VFPJUDEEHZWETZYVGWHKKQETGFQJNCE"
    "GGWHKK?DQMCPFQZDQMMIAGPFXHQRLG"
    "TIMVMZJANQLVKQEDAGDVFRPJUNGEUNA"
    "QZGZLECGYUXUEENJTBJLBQCRTBJDFHRR"
    "YIZETKZEMVDUFKSJHKFWHKUWQLSZFTI"
    "HHDDDUVH?DWKBFUFPWNTDFIYCUQZERE"
    "EVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDX"
    "FLGGTEZ?FKZBSFDQVGOGIPUFXHHDRKF"
    "FHQNTGPUAECNUVPDJMQCLQUMUNEDFQ"
    "ELZZVRRGKFFVOEEXBDMVPNFQXEZLGRE"
    "DNQFMPNZGLFLPMRJQYALMGNUVPDXVKP"
    "DQUMEBEDMHDAFMJGZNUPLGEWJLLAETG"
)

K3_CIPHERTEXT = (
    "ENDYAHR0HNLSRHEOCPTEOIBIDYSHNAIA"
    "CHTNREYULDSLLSLLNOHSNOSMRWXMNE"
    "TPRNGATIHNRARPESLNNELEBLPIIACAE"
    "WMTWNDITEENRAHCTENEUDRETNHAEOE"
    "TFOLSEDTIWENHAEIOYTEYQHEENCTAYCR"
    "EIFTBRSPAMHHEWENATAMATEGYEERLB"
    "TEEFOASFIOTUETUAEOTOARMAEERTNRTI"
    "BSEDDNIAAHTTMSTEWPIEROAGRIEWFEB"
    "AECTDDHILCEIHSITEGOEAOSDDRYDLORIT"
    "RKLMLEHAGTDHARDPNEOHMGFMFEUHE"
    "ECDMRIPFEIMEHNLSSTTRTVDOHW?"
).replace("0", "O")  # correct OCR confusion of letter O and digit 0

K4_CIPHERTEXT = (
    "OBKR"
    "UOXOGHULBSOLIFBBWFLRVQQPRNGKSSO"
    "TWTQSJQSSEKZZWATJKLUDIAWINFBNYP"
    "VTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
)

# Known plaintext solutions (misspellings preserved) from Rumkin.com【989426088448438†L8-L20】【450144964858183†L49-L64】【228526962033129†L31-L41】
K1_PLAINTEXT = (
    "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT "
    "LIES THE NUANCE OF IQLUSION"
)

K2_PLAINTEXT = (
    "IT WAS TOTALLY INVISIBLE HOWS THAT POSSIBLE? "
    "THEY USED THE EARTHS MAGNETIC FIELD X "
    "THE INFORMATION WAS GATHERED AND TRANSMITTED "
    "UNDERGRUUND TO AN UNKNOWN LOCATION X "
    "DOES LANGLEY KNOW ABOUT THIS? "
    "THEY SHOULD ITS BURIED OUT THERE SOMEWHERE X "
    "WHO KNOWS THE EXACT LOCATION? "
    "ONLY WW THIS WAS HIS LAST MESSAGE X "
    "THIRTY EIGHT DEGREES FIFTY SEVEN MINUTES SIX POINT FIVE SECONDS NORTH "
    "SEVENTY SEVEN DEGREES EIGHT MINUTES FORTY FOUR SECONDS WEST X "
    "LAYER TWO"
)

K3_PLAINTEXT = (
    "SLOWLY DESPARATLY SLOWLY THE REMAINS OF PASSAGE DEBRIS "
    "THAT ENCUMBERED THE LOWER PART OF THE DOORWAY WAS REMOVED "
    "WITH TREMBLING HANDS I MADE A TINY BREACH IN THE UPPER LEFT HAND CORNER "
    "AND THEN WIDENING THE HOLE A LITTLE I INSERTED THE CANDLE AND PEERED IN "
    "THE HOT AIR ESCAPING FROM THE CHAMBER CAUSED THE FLAME TO FLICKER BUT PRESENTLY "
    "DETAILS OF THE ROOM WITHIN EMERGED FROM THE MIST X CAN YOU SEE ANYTHING Q?"
)

################################################################################
# Utility functions
################################################################################

def clean_text(text: str) -> str:
    """Remove non‑alphabetic characters and convert to uppercase."""
    return ''.join(ch for ch in text.upper() if ch.isalpha())


def vigenere_encrypt(plaintext: str, key: str, alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ") -> str:
    """Encrypt plaintext using a standard Vigenère cipher with the given key.

    Only letters in the alphabet are encrypted; other characters are passed
    through unchanged.
    """
    key = clean_text(key)
    alphabet_size = len(alphabet)
    key_indices = [alphabet.index(k) for k in key]
    result = []
    j = 0
    for ch in plaintext:
        if ch.upper() in alphabet:
            idx = alphabet.index(ch.upper())
            shift = key_indices[j % len(key_indices)]
            enc_idx = (idx + shift) % alphabet_size
            result.append(alphabet[enc_idx])
            j += 1
        else:
            result.append(ch)
    return ''.join(result)


def vigenere_decrypt(ciphertext: str, key: str, alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ") -> str:
    """Decrypt a Vigenère cipher given the key."""
    key = clean_text(key)
    alphabet_size = len(alphabet)
    key_indices = [alphabet.index(k) for k in key]
    result = []
    j = 0
    for ch in ciphertext:
        if ch.upper() in alphabet:
            idx = alphabet.index(ch.upper())
            shift = key_indices[j % len(key_indices)]
            dec_idx = (idx - shift) % alphabet_size
            result.append(alphabet[dec_idx])
            j += 1
        else:
            result.append(ch)
    return ''.join(result)


def decode_k1() -> str:
    """Return the plaintext for K1 by applying the known Vigenère keys."""
    # The tableau on the sculpture is keyed with "KRYPTOS".  The cipher key
    # discovered through frequency analysis is "PALIMPSEST"【989426088448438†L8-L20】.
    alphabet_key = "KRYPTOSABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # Build the keyed alphabet by removing duplicate letters while preserving order.
    seen = set()
    keyed_alphabet = []
    for ch in alphabet_key:
        if ch not in seen and ch.isalpha():
            keyed_alphabet.append(ch)
            seen.add(ch)
    keyed_alphabet = ''.join(keyed_alphabet)
    return vigenere_decrypt(K1_CIPHERTEXT, key="PALIMPSEST", alphabet=keyed_alphabet)


def decode_k2() -> str:
    """Return the plaintext for K2 using the known Vigenère keys."""
    alphabet_key = "KRYPTOSABCDEFGHIJKLMNOPQRSTUVWXYZ"
    seen = set()
    keyed_alphabet = []
    for ch in alphabet_key:
        if ch not in seen and ch.isalpha():
            keyed_alphabet.append(ch)
            seen.add(ch)
    keyed_alphabet = ''.join(keyed_alphabet)
    return vigenere_decrypt(K2_CIPHERTEXT.replace('?', ''), key="ABSCISSA", alphabet=keyed_alphabet)


def chunk_string(text: str, chunk_len: int) -> List[str]:
    """Split a string into equal sized chunks.  The last chunk may be shorter."""
    return [text[i:i + chunk_len] for i in range(0, len(text), chunk_len)]


def columnar_transpose(text: str, n_columns: int) -> str:
    """Perform a simple columnar transposition.

    Arrange the text row‑wise into a matrix with the specified number of
    columns, then read down the columns from right to left to form the
    transposed text.
    """
    rows = chunk_string(text, n_columns)
    # Pad the final row if necessary
    if len(rows[-1]) < n_columns:
        rows[-1] += 'X' * (n_columns - len(rows[-1]))
    result = []
    for c in reversed(range(n_columns)):
        for r in rows:
            result.append(r[c])
    return ''.join(result)


def decode_k3() -> str:
    """Decode K3 using a double columnar transposition.

    The NSA solution uses matrix sizes 4×86 and 28×? for the two transpositions.
    Here we implement the description from Rumkin.com【228526962033129†L31-L41】.  This
    function is provided for illustration and does not recompute the key; it
    simply reverses the process described by Gillogly.
    """
    # Strip non‑alphabetic characters
    text = clean_text(K3_CIPHERTEXT.replace('?', ''))
    # First transposition: read columns of a 21‑column matrix (rows of length 21)
    first = columnar_transpose(text, 21)
    # Second transposition: now read columns of a 28‑column matrix
    second = columnar_transpose(first, 28)
    return second


################################################################################
# Gradient descent demonstration for simple substitution ciphers
################################################################################

class SubstitutionCipherModel:
    """A simple model that tries to learn a substitution mapping from cipher
    letters to plaintext letters by optimising a differentiable score.

    The model uses a parameter vector of size 26×26 representing a weight for
    mapping cipher letter i to plain letter j.  A softmax over each row
    produces a probability distribution for each cipher letter.  The cost
    function encourages mappings that produce high scores under an English
    language model (here a simple bigram frequency model).

    Note: This is an experimental demonstration and not suitable for
    production cryptanalysis.  It treats the substitution as a noisy
    probability distribution and optimises via gradient descent.  For K4,
    the cipher may not even be a simple substitution cipher, so this
    technique is speculative.
    """

    def __init__(self, cipher_text: str, weights: Dict[str, float], lr: float = 0.5):
        self.cipher_text = clean_text(cipher_text)
        self.weights = weights  # bigram weights from language model
        # Parameters: matrix of logits for mapping cipher letter i to plain letter j
        self.params = [[random.random() for _ in range(26)] for _ in range(26)]
        self.lr = lr

    def _softmax_row(self, row: List[float]) -> List[float]:
        m = max(row)
        exps = [math.exp(x - m) for x in row]
        total = sum(exps)
        return [v / total for v in exps]

    def decode_probs(self) -> List[List[float]]:
        """Return a 26×26 matrix of probabilities via softmax on each row."""
        return [self._softmax_row(row) for row in self.params]

    def sample_mapping(self) -> Dict[str, str]:
        """Sample a deterministic mapping from the current probability
        distributions by taking the highest‑probability output for each cipher
        letter.  The result may not be a valid permutation if two cipher
        letters map to the same plain letter.
        """
        probs = self.decode_probs()
        mapping: Dict[str, str] = {}
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        taken = set()
        for i, p in enumerate(probs):
            # choose the highest scoring plain letter that isn't yet taken
            sorted_candidates = sorted(range(26), key=lambda j: p[j], reverse=True)
            for j in sorted_candidates:
                letter = alphabet[j]
                if letter not in taken:
                    mapping[alphabet[i]] = letter
                    taken.add(letter)
                    break
        return mapping

    def _decode_with_mapping(self, mapping: Dict[str, str]) -> str:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return ''.join(mapping.get(ch, ch) for ch in self.cipher_text)

    def _evaluate(self, decoded: str) -> float:
        """Compute an average bigram weight over the decoded text."""
        pairs = [decoded[i:i+2] for i in range(len(decoded) - 1)]
        total = 0.0
        for duo in pairs:
            total += self.weights.get(duo, 0.0)
        return total / (len(decoded) - 1)

    def step(self) -> float:
        """Perform a single gradient descent step and return the current score.

        The gradient is computed approximately by taking the partial derivative
        of the cost function with respect to each logit.  Because the cost
        surface is extremely complex and the mapping is discrete, this method
        uses a REINFORCE‑like trick: sample a mapping based on the current
        probabilities, evaluate it, and then nudge the parameters towards the
        sampled choices proportional to the score.  This is a form of
        stochastic gradient ascent (hill‑climbing) where the objective is to
        maximise the bigram score.
        """
        probs = self.decode_probs()
        mapping_indices: Dict[int, int] = {}
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        taken = set()
        # sample mapping greedily for gradient estimate
        for i, p in enumerate(probs):
            sorted_candidates = sorted(range(26), key=lambda j: p[j], reverse=True)
            for j in sorted_candidates:
                if j not in taken:
                    mapping_indices[i] = j
                    taken.add(j)
                    break
        # decode text
        decoded = ''.join(alphabet[mapping_indices.get(alphabet.index(ch), 0)] for ch in self.cipher_text)
        score = self._evaluate(decoded)
        # approximate gradient ascent: encourage the chosen mappings
        for i in mapping_indices:
            j = mapping_indices[i]
            # update logit for mapping cipher letter i to plain letter j
            self.params[i][j] += self.lr * score
        return score


def load_bigram_weights(path: str) -> Dict[str, float]:
    """Load bigram counts from a file and convert to weights.

    The input file should contain one two‑letter sequence per line followed by
    its count, separated by whitespace, e.g. "TH 309".  We normalise the
    weights by dividing by a constant so that scores are manageable.
    """
    weights = {}
    with open(path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                bigram, count = parts
                weights[bigram.upper()] = int(count) / 1e7
    return weights


if __name__ == "__main__":
    # Demonstration of decryption functions
    print("K1 decrypted:\n", decode_k1())
    print("\nK2 decrypted (first 200 chars):\n", decode_k2()[:200], "...")
    # The double transposition for K3 yields a continuous string; adding spaces
    # manually would improve readability.
    print("\nK3 decrypted (first 200 chars):\n", decode_k3()[:200], "...")

    # Gradient descent demo (optional):
    # To run this demonstration, download an English bigram weight file such
    # as count_2l.txt from Peter Norvig's corpus and call load_bigram_weights
    # before creating the model.  We perform a few iterations to illustrate
    # how the score improves.  This will not solve K4 but shows the idea.
    try:
        weights = load_bigram_weights("count_2l.txt")
        model = SubstitutionCipherModel(K4_CIPHERTEXT, weights, lr=0.1)
        for iteration in range(10):
            score = model.step()
            if iteration % 2 == 0:
                mapping = model.sample_mapping()
                decoded_sample = model._decode_with_mapping(mapping)
                print(f"Iter {iteration}, score={score:.4f}, sample decode snippet: {decoded_sample[:50]}")
    except FileNotFoundError:
        print("Bigram weight file not found. Skip gradient descent demo.")
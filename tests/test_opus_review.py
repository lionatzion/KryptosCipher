"""Controls for the Opus review code: soundness, published cross-checks, real data."""
import random
import unittest

from research import k4_core
from research.opus_review import audit, keyword_tableau as kt
from research.opus_review.core import (
    ABC, CRIBS, CRIB_POSITIONS, K4, KA, QuagmireGraph, affine_keys, crib_relations,
    keyword_alphabet, lagged_fibonacci, periodic_any_alphabets, periodic_latin_square,
)


class CoreTests(unittest.TestCase):
    def test_inputs_match_astra(self):
        self.assertEqual(K4, k4_core.CIPHER)
        self.assertEqual(CRIBS, k4_core.CRIBS)

    def test_keyword_alphabets(self):
        self.assertEqual(keyword_alphabet("KRYPTOS"), KA)
        for mode in kt.MODES:
            for word in ("KRYPTOS", "ZEBRA", "A", "PALIMPSEST", "BERLINCLOCK"):
                self.assertEqual(sorted(keyword_alphabet(word, mode)), list(ABC))

    def test_bean_relations(self):
        equal, unequal = crib_relations()
        self.assertEqual(equal, [(27, 65)])  # 1-based 28 and 66: plain R -> cipher P
        self.assertEqual(len(unequal), 22)
        self.assertEqual(sorted({j - i for i, j in unequal}), [1, 3, 4, 5, 7, 9, 34, 42, 43, 45, 50])

    def test_quagmire_solver_never_rejects_a_planted_instance(self):
        rng = random.Random(7)
        for _ in range(300):
            pa, ca = "".join(rng.sample(ABC, 26)), "".join(rng.sample(ABC, 26))
            key = [rng.randrange(26) for _ in range(97)]
            plain = [rng.choice(ABC) for _ in range(97)]
            for i, ch in CRIBS.items():
                plain[i] = ch
            cipher = "".join(ca[(pa.index(p) + k) % 26] for p, k in zip(plain, key))
            self.assertTrue(QuagmireGraph(cipher).feasible({i: key[i] for i in CRIBS}))

    def test_quagmire_solver_accepts_fixed_tableaux_and_beaufort(self):
        graph = QuagmireGraph()
        for pa, ca in ((ABC, ABC), (KA, KA), (ABC, KA), (KA, ABC)):
            self.assertTrue(graph.feasible(affine_keys(pa, ca, 1)))
            self.assertTrue(graph.feasible(affine_keys(pa, ca, 25)))  # c = k - p, relabel p -> -p

    def test_gromark_counts_match_bean_2021(self):
        graph = QuagmireGraph()
        survivors = [p for p in audit.all_primers(10, 5) if any(p)
                     and graph.feasible(dict(zip(CRIB_POSITIONS, (lagged_fibonacci(p, 10, 74)[i]
                                                                  for i in CRIB_POSITIONS))))]
        self.assertEqual(len(survivors), 39)
        self.assertIn((2, 6, 7, 1, 7), survivors)

    def test_period_ladder_examples(self):
        graph = QuagmireGraph()
        self.assertFalse(periodic_any_alphabets(7)[0])     # positions 66/73 share residue
        self.assertTrue(periodic_any_alphabets(11)[0])
        self.assertFalse(periodic_latin_square(11)[0])     # forced 28/66 merge creates a conflict
        status, witness = graph.periodic(8)
        self.assertEqual(status, "feasible")
        pa, ca, rk = witness["plain_alphabet"], witness["cipher_alphabet"], witness["residue_keys"]
        for i, p in CRIBS.items():
            self.assertEqual(ca[(pa.index(p) + rk[i % 8]) % 26], K4[i])

    def test_sculpture_texts(self):
        _, provenance, extra = audit.sculpture_texts()
        self.assertEqual((provenance["K2_correction_insert_0b"], provenance["K2_correction_letter"]), (361, "S"))
        self.assertTrue(extra["K2_plain_corrected"].endswith("WESTXLAYERTWO"))
        self.assertTrue(extra["K3_plain"].startswith("SLOWLYDESPARATLYSLOWLY"))
        self.assertTrue(extra["K3_plain"].endswith("CANYOUSEEANYTHINGQ"))

    def test_recurrence_brute_force_finds_planted(self):
        coeff, order = [3, 0, 7, 11], 3
        seq = [5, 9, 2]
        while len(seq) < 97:
            seq.append((coeff[-1] + sum(coeff[j] * seq[-1 - j] for j in range(order))) % 26)
        for q in (2, 13):
            km = {i: seq[i] % q for i in CRIBS}
            self.assertTrue(audit._forward_ok(km, [c % q for c in coeff], order, q))


class KeywordTableauTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        words = kt.DICTIONARY.read_text().split()
        rng = random.Random(3)
        cls.family = kt.alphabet_family(rng.sample(words, 3000) + list(kt.CONTEXT_WORDS))
        cls.pos = kt.positions_matrix(cls.family[0])
        cls.pool = audit.sculpture_texts()[2]["K1K2K3_plain_corrected"]

    def test_real_k1_k2_controls(self):
        for row in kt.real_positive_controls(self.family, self.pos):
            self.assertTrue(row.get("recovered_p8", row.get("recovered_p10")), row)

    def test_planted_periodic_and_gromark(self):
        rng = random.Random(11)
        for period in (8, 13, 16, 24, 5):
            self.assertTrue(kt.planted_s1(self.family, self.pos, rng, self.pool, period)["recovered"])
        for _ in range(4):
            self.assertTrue(kt.planted_s2(self.family, self.pos, rng, self.pool)["recovered"])

    def test_round_trip_all_signs(self):
        rng = random.Random(5)
        plain = "".join(rng.choice(ABC) for _ in range(97))
        shifts = [rng.randrange(26) for _ in range(97)]
        for sign in kt.NUMERIC_SIGNS:
            cipher = kt.encrypt(plain, shifts, KA, ABC, sign)
            self.assertEqual(kt.decrypt(cipher, shifts, KA, ABC, sign), plain)

    def test_gromark_full_key_inverts_recurrence(self):
        key = lagged_fibonacci([3, 1, 4, 1, 5], 10, 97)
        self.assertEqual(kt.gromark_full_key(key[21:34], 10, 5), key)


if __name__ == "__main__":
    unittest.main()

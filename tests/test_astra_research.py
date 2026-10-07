"""Positive controls and adversarial checks for exact K4 experiment logic."""
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import kryptos_k4_p27_sweep as legacy
import kryptos_k4_p27_sweep_phased as phased
from research.k4_core import (
    ABC, KA, CIPHER, CRIBS, candidate_check, decrypt, encrypt, enumerate_field,
    feedback_constraints, implied_keys, linear_solutions, periodic_constraints,
    recurrence_candidates, systems,
)
from research.run_astra import blind_score, source_texts


class ExactArithmeticTests(unittest.TestCase):
    def test_canonical_inputs(self):
        self.assertEqual(len(CIPHER), 97)
        self.assertEqual(CIPHER, legacy.CIPHERTEXT)
        self.assertEqual(len(CRIBS), 24)
        self.assertEqual([CIPHER[s-1:s-1+len(w)] for s, w in legacy.ISLANDS],
                         ["FLRV", "QQPRNGKSS", "NYPVTT", "MZFPK"])

    def test_all_affine_systems_roundtrip_and_tamper(self):
        for _, pa, ca, a in systems():
            keys = [(i * i + 3 * i + 7) % 26 for i in range(97)]
            plain = decrypt(CIPHER, keys, pa, ca, a)
            self.assertEqual(encrypt(plain, keys, pa, ca, a), CIPHER)
        keys = [implied_keys().get(i, i % 26) for i in range(97)]
        plain = decrypt(CIPHER, keys)
        self.assertTrue(candidate_check(plain, encrypt(plain, keys))["consistent"])
        self.assertFalse(candidate_check(plain, encrypt(plain, keys))["is_solution"])
        self.assertFalse(candidate_check(plain, "A" + CIPHER[1:])["consistent"])
        self.assertFalse(candidate_check(plain[:-1], CIPHER)["consistent"])

    def test_p27_fit_is_vacuous_for_any_observations(self):
        # Even arbitrarily altered ciphertext has exactly the same lack of collisions.
        for cipher in (CIPHER, "A" * 97, CIPHER[::-1]):
            values, conflicts = periodic_constraints(implied_keys(cipher), 27)
            self.assertEqual(len(values), 24)
            self.assertFalse(conflicts)
        values, _ = periodic_constraints(implied_keys(), 27)
        self.assertEqual(sorted(set(range(27)) - set(values)), [7, 8, 20])
        self.assertEqual(implied_keys()[32], 0)
        self.assertEqual(implied_keys()[73], 0)

    def test_phase_is_relabeling_in_existing_code(self):
        base = [ABC[(i * 7 + 3) % 26] for i in range(27)]
        plain = legacy.decrypt_with_keystream(CIPHER, base)
        for phase in range(27):
            rotated = [base[(i - phase) % 27] for i in range(27)]
            self.assertEqual(phased.decrypt_with_keystream(CIPHER, rotated, phase), plain)
            values = phased.derive_constraints_from_islands(
                CIPHER, legacy.ISLANDS, 27, phase)
            self.assertEqual(len(values), 24)

    def test_phased_cli_records_reproducible_phase(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, "kryptos_k4_p27_sweep_phased.py",
                                     "--phase", "1", "--letters", "AB", "--topn", "5",
                                     "--outdir", directory], capture_output=True, text=True, check=True)
            self.assertIn("candidates that satisfy islands: 8", result.stdout)
            rows = json.loads((Path(directory) / "k4_top10_summary.json").read_text())
            for row in rows:
                self.assertEqual(row["phase"], 1)
                self.assertEqual(phased.decrypt_with_keystream(
                    CIPHER, row["keystream_27"], row["phase"]), row["plaintext"])

    def test_short_period_conflict_and_long_period_collision_gap(self):
        keys = implied_keys()
        for period in range(1, 27):
            self.assertTrue(periodic_constraints(keys, period)[1])
        for period in (27, 28, 29):
            self.assertFalse(periodic_constraints(keys, period)[1])
        for period in range(30, 53):
            self.assertTrue(periodic_constraints(keys, period)[1])

    def test_progressive_positive_control(self):
        base, period, phase, drift = [7, 3, 21, 9, 5], 5, 3, 7
        keys = {i: (base[(i + phase) % period] + drift * ((i + phase) // period)) % 26
                for i in range(97)}
        values, conflicts = periodic_constraints(keys, period, phase, drift)
        self.assertEqual(values, dict(enumerate(base)))
        self.assertFalse(conflicts)
        self.assertTrue(periodic_constraints(keys, period, phase, drift + 1)[1])

    def test_crt_solver_matches_bruteforce_nonunit_matrix(self):
        rows, rhs = [[2, 0], [0, 2]], [2, 4]
        s2 = linear_solutions(rows, rhs, 2, 2)
        s13 = linear_solutions(rows, rhs, 2, 13)
        actual = {tuple((13 * a + 14 * b) % 26 for a, b in zip(x, y))
                  for x in enumerate_field(s2, 2) for y in enumerate_field(s13, 13)}
        expected = {x for x in itertools.product(range(26), repeat=2)
                    if all(sum(a*b for a, b in zip(row, x)) % 26 == b
                           for row, b in zip(rows, rhs))}
        self.assertEqual(actual, expected)
        self.assertIsNone(linear_solutions([[0]], [1], 1, 2))

    def test_recurrence_recovers_hidden_control(self):
        coeff = [3, 5, 7]
        seq = [11, 2]
        for _ in range(95):
            seq.append((coeff[0] * seq[-1] + coeff[1] * seq[-2] + coeff[2]) % 26)
        observed = {i: seq[i] for i in CRIBS}
        result = recurrence_candidates(observed, 2)
        self.assertTrue(result["complete"])
        self.assertIn(coeff, result["survivors"])

    def test_recurrence_cap_does_not_claim_elimination(self):
        result = recurrence_candidates({i: i % 26 for i in range(8)}, 8, cap=2)
        self.assertFalse(result["complete"])
        self.assertEqual(result["rejection_stage"], "enumeration_cap")

    def test_feedback_synthetic_controls_all_signs_and_alphabets(self):
        plain = "".join(ABC[(i * i + i * 3 + 4) % 26] for i in range(97))
        for pa, ca, a, b in itertools.product((ABC, KA), (ABC, KA), (1, 25), (1, 25)):
            lag, shift = 8, 7
            cipher = "".join(ca[(a * pa.index(p) +
                             (b * pa.index(plain[i-lag]) + shift if i >= lag else 0)) % 26]
                             for i, p in enumerate(plain))
            observed = dict(enumerate(plain))
            result = feedback_constraints(cipher, observed, lag, a, b, shift, pa, ca)
            self.assertIsNotNone(result)
            self.assertEqual(result["forced_plaintext"], plain)
            # One later ciphertext error must violate a fully observed chain.
            changed = cipher[:30] + ca[(ca.index(cipher[30]) + 1) % 26] + cipher[31:]
            self.assertIsNone(feedback_constraints(changed, observed, lag, a, b, shift, pa, ca))

    def test_sculpture_streams_and_known_key_positive_controls(self):
        texts = source_texts()
        self.assertEqual([len(texts[n]) for n in ("K1_cipher", "K2_cipher", "K3_cipher")],
                         [63, 369, 336])
        for source, target, word in (("K1_plain", "K1_cipher", "PALIMPSEST"),
                                     ("K2_plain_as_inscribed", "K2_cipher", "ABSCISSA")):
            plain = texts[source]
            key = [KA.index(word[i % len(word)]) for i in range(len(plain))]
            self.assertEqual(encrypt(plain, key, KA, KA), texts[target])

    def test_scoring_does_not_reward_cribs_or_windows_touching_them(self):
        plain = "A" * 97
        changed = list(plain)
        for i, p in CRIBS.items():
            changed[i] = p
        self.assertEqual(blind_score(plain), blind_score("".join(changed)))


if __name__ == "__main__":
    unittest.main()

"""Guard source-specific export claims and exact period-24 witnesses."""
import json
from pathlib import Path
import unittest

from kryptos.constants import STD, K4_CIPHERTEXT
from research.review_checks import classify_row, run_audit
from route_transposition import route_east_then_ne


class ReviewChecks(unittest.TestCase):
    def test_repository_export_counts_and_saved_audit(self):
        actual = run_audit()
        self.assertEqual(actual, json.loads(Path("out/november_20261123/review_checks.json").read_text()))
        self.assertEqual(actual["summary"], {"rows": 267, "phase_26_rows": 110,
                                           "phase_0_rows": 155, "invalid_or_incomplete_rows": 2})
        self.assertTrue(actual["duplicated_reproduction_artifacts"]["byte_identical"])

    def test_phase_convention_and_highlighted_field(self):
        key = "ABCDEFGHIJKLMNOPQRSTUVWXYZA"
        for phase in (0, 1, 26):
            plain = "".join(STD[(STD.index(c) - STD.index(key[(i + phase) % 27])) % 26]
                            for i, c in enumerate(K4_CIPHERTEXT))
            result = classify_row({"Keystream_27": key, "Plaintext_highlighted": plain})
            self.assertEqual(result["matching_phases"], [phase])
            altered = ("B" if plain[0] == "A" else "A") + plain[1:]
            self.assertEqual(classify_row({"keystream_27": key, "plaintext": altered})["status"], "does_not_reproduce")

    def test_placeholders_are_not_candidates(self):
        self.assertEqual(classify_row({"keystream_27": "A" * 27, "plaintext": "...EAST..."})["status"], "invalid_length_or_characters")
        self.assertEqual(classify_row({"keystream_27": "A" * 27})["status"], "missing_plaintext_or_key")

    def test_five_conflicts_in_all_six_modes(self):
        witnesses = run_audit()["period24_witnesses"]
        self.assertEqual(len(witnesses), 6)
        for row in witnesses:
            self.assertEqual([p["positions_1_based"] for p in row["pairs"]],
                             [[i, i + 48] for i in range(22, 27)])
            self.assertTrue(all(p["conflict"] and p["same_residue_mod_24"] for p in row["pairs"]))

    def test_unimplemented_historical_route_does_not_fake_geometry(self):
        with self.assertRaises(NotImplementedError):
            route_east_then_ne(7, 14, 97)


if __name__ == "__main__":
    unittest.main()

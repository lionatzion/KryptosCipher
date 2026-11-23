"""Known answers, novel seeded controls, and adversarial audit regressions."""
from collections import Counter
from contextlib import redirect_stdout
import io
from itertools import product
import json
from pathlib import Path
import random
import tempfile
import unittest

import jsonschema

from kryptos.cli import main, source_hash
from kryptos.constants import (ANCHORS, FIT_ANCHORS, HOLDOUT_ANCHORS, K4_CIPHERTEXT,
                               K2_CIPHERTEXT, K3_CIPHERTEXT, KRYPTOS, STD)
from kryptos.diagnostics import crib_parity, matched_controls, width_bigrams
from kryptos.primitives import (MODES, corrected_k2, decode_k2, decode_k3,
                                encode_k3, inverse_permutation, remove_positions,
                                rotate, route_catalog, transform, verify_baselines)
from kryptos.scoring import QuadgramScorer, window_groups
from kryptos.solver import (Model, clock_schedules, completions, decrypt, encrypt,
                            fixed_key_matches, infer_key, search)

SYNTHETIC = ("FROMTHEGATEYOUCANLOOKEASTNORTHEASTTOSEETHEHIDDENMESSAGEBYTHEOLD"
             "BERLINCLOCKANDWAITFORTHENEXTSIGNAL")


class BaselineTests(unittest.TestCase):
    def test_exact_known_answers_and_roundtrips(self):
        self.assertEqual(verify_baselines(), {"K1": True, "K2_carved": True, "K2_corrected": True, "K3": True})
        self.assertEqual(len(K4_CIPHERTEXT), 97)
        self.assertEqual(len(ANCHORS), 24)

    def test_physical_k2_correction_is_explicit(self):
        self.assertEqual(len(K2_CIPHERTEXT), 372)
        self.assertEqual(corrected_k2()[358:365], "NUPLGES")
        self.assertEqual(remove_positions(corrected_k2(), [364]), K2_CIPHERTEXT)
        self.assertTrue(decode_k2().endswith("WESTIDBYROWS"))
        self.assertTrue(decode_k2(True).endswith("WESTXLAYERTWO"))
        self.assertEqual(decode_k2().count("?"), 3)

    def test_rotation_independent_small_example(self):
        self.assertEqual(rotate("ABCDEF", 3), "CFBEAD")
        self.assertEqual(rotate("ABCDEF", 3, True), "DAEBFC")
        self.assertEqual(encode_k3(decode_k3()), K3_CIPHERTEXT)
        with self.assertRaises(ValueError):
            rotate("ABCDE", 3)

    def test_novel_rotational_isomorphs(self):
        rng = random.Random(2718)
        for _ in range(8):
            plaintext = "".join(rng.choice(STD) for _ in range(336)) + "?"
            encrypted = encode_k3(plaintext)
            self.assertEqual(rotate(rotate(encrypted[:-1], 24), 8) + "?", plaintext)

    def test_modes_do_not_advance_on_punctuation(self):
        for alphabet, mode in product((STD, KRYPTOS), MODES):
            encrypted = transform("AA?AA", [1, 3], alphabet, mode)
            self.assertEqual(encrypted[:2], encrypted[3:])
            self.assertEqual(transform(encrypted, [1, 3], alphabet, mode, True), "AA?AA")
        for key in ([], [None], [26], [-1]):
            with self.assertRaises(ValueError):
                transform("AAA", key)


class SolverControls(unittest.TestCase):
    def test_novel_seeded_controls_both_orders_all_modes(self):
        rng = random.Random(20261123)
        routes = list(route_catalog(max_column_width=3))
        for trial, (alphabet, mode, order) in enumerate(product((STD, KRYPTOS), MODES, ("S_T", "T_S"))):
            plain = list("".join(rng.choice(STD) for _ in range(97)))
            for i, p in ANCHORS.items():
                plain[i] = p
            plain = "".join(plain)
            name, route = routes[(trial * 7 + 3) % len(routes)]
            key = tuple(rng.randrange(26) for _ in range(5))
            model = Model(name, len(key), route, alphabet, mode, order)
            cipher = encrypt(plain, key, model)
            fit = infer_key(cipher, model)
            self.assertTrue(fit["compatible"])
            self.assertTrue(all(k is None or k == key[i] for i, k in enumerate(fit["key"])))
            result = search(cipher, [model], max_per_model=10000, max_total=10000, top=10000)
            self.assertTrue(result["complete"])
            self.assertIn((key, plain), [(c["key"], c["plaintext"]) for c in result["candidates"]])
            self.assertEqual(decrypt(cipher, key, model), plain)
            # Corrupt an anchor paired to a previously observed residue.
            inv = inverse_permutation(route)
            slots = {}
            for i in ANCHORS:
                j = inv[i]
                residue = (i if order == "S_T" else j) % 5
                if residue in slots:
                    changed = cipher[:j] + alphabet[(alphabet.index(cipher[j]) + 1) % 26] + cipher[j + 1:]
                    self.assertFalse(infer_key(changed, model)["compatible"])
                    break
                slots[residue] = j

    def test_zero_collision_valid_model_is_retained(self):
        cuts = (0, 21, 37, 49, 59, 75, 97)
        blocks = [list(range(a, b)) for a, b in zip(cuts, cuts[1:])]
        route = tuple(i for b in (1, 0, 2, 3, 5, 4) for i in blocks[b])
        model = Model("zero-collision-control", 24, route, order="T_S")
        key = tuple(range(24))
        cipher = encrypt(SYNTHETIC, key, model)
        self.assertEqual(infer_key(cipher, model)["consistency_checks"], 0)
        result = search(cipher, [model])
        self.assertEqual(result["candidates"][0]["plaintext"], SYNTHETIC)
        self.assertTrue(result["complete"])

    def test_partial_keys_are_enumerated_or_reported_incomplete(self):
        model = Model("p27", 27, tuple(range(97)))
        fit = infer_key(K4_CIPHERTEXT, model)
        self.assertEqual(fit["free_residues"], [7, 8, 20])
        self.assertEqual(fit["completion_count"], 17576)
        result = search(K4_CIPHERTEXT, [model], max_per_model=3)
        self.assertFalse(result["complete"])
        self.assertEqual(result["evaluated_completions"], 3)
        self.assertEqual(len({c["key"] for c in result["candidates"]}), 3)
        self.assertEqual(list(completions([1, None, 2], 26))[-1], (1, 25, 2))
        zero = search(K4_CIPHERTEXT, [model], max_total=0)
        self.assertFalse(zero["complete"])
        self.assertEqual(zero["candidates"], [])

    def test_fitted_and_evaluation_holdout_are_separate(self):
        model = Model("control", 5, tuple(range(97)))
        key = (1, 4, 2, 8, 5)
        cipher = encrypt(SYNTHETIC, key, model)
        result = search(cipher, [model], fit_anchors=FIT_ANCHORS, holdout_anchors=HOLDOUT_ANCHORS)
        self.assertEqual(result["candidates"][0]["holdout_matches"], 11)
        wrong = dict(HOLDOUT_ANCHORS)
        wrong[63] = "Z"
        altered = search(cipher, [model], fit_anchors=FIT_ANCHORS, holdout_anchors=wrong)
        self.assertEqual(result["candidates"][0]["key"], altered["candidates"][0]["key"])
        self.assertEqual(altered["candidates"][0]["holdout_matches"], 10)
        with self.assertRaises(ValueError):
            search(cipher, [model], holdout_anchors=ANCHORS)

    def test_every_catalog_route_is_bijective_and_has_inverse(self):
        routes = list(route_catalog(max_column_width=4))
        values = {p for _, p in routes}
        self.assertEqual(len(values), len(routes))
        for route in values:
            self.assertEqual(sorted(route), list(range(97)))
            self.assertIn(inverse_permutation(route), values)
        with self.assertRaises(ValueError):
            Model("bad-route", 5, (0,) * 97)

    def test_indexed_nulls_keep_other_occurrences(self):
        self.assertEqual(remove_positions("WAWBW", [0, 4]), "AWB")
        with self.assertRaises(ValueError):
            remove_positions("AAA", [1, 1])

    def test_independently_fixed_clock_keys(self):
        schedules = list(clock_schedules())
        self.assertEqual(len({k for _, k in schedules}), len(schedules))
        route = next(p for n, p in route_catalog() if n != "identity")
        for order in ("S_T", "T_S"):
            model = Model("clock-control", 24, route, KRYPTOS, "beaufort", order)
            key = schedules[17][1]
            cipher = encrypt(SYNTHETIC, key, model)
            self.assertTrue(fixed_key_matches(cipher, model, key))
            wrong = tuple((k + 1) % 26 for k in key)
            self.assertFalse(fixed_key_matches(cipher, model, wrong))


class ScoringAndCalibrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "test-only-quadgrams.txt"
        # A tiny synthetic test table, expressly not an English research corpus.
        counts = Counter(SYNTHETIC[i:i + 4] for i in range(94))
        self.path.write_text("".join(f"{g} {n}\n" for g, n in sorted(counts.items())))
        self.scorer = QuadgramScorer(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_split_windows_and_anchor_score_contamination(self):
        groups = window_groups()
        self.assertEqual({k: len(v) for k, v in groups.items()},
                         {"unknown_only": 64, "boundary": 12, "anchor_internal": 18, "full": 94})
        self.assertEqual(set(groups["unknown_only"]) & set(groups["boundary"]), set())
        changed = list(SYNTHETIC)
        for i in ANCHORS:
            changed[i] = "Z"
        a, b = self.scorer.score(SYNTHETIC), self.scorer.score("".join(changed))
        self.assertEqual(a["unknown_only"], b["unknown_only"])
        self.assertNotEqual(a["boundary"], b["boundary"])
        self.assertNotEqual(a["full"], b["full"])
        with self.assertRaises(ValueError):
            self.scorer.score(SYNTHETIC[:-1] + "?")

    def test_bad_corpus_tables_fail_loudly(self):
        for text in ("", "AAAA 0", "AAAA nan", "AAAA inf", "AAA 3", "AAAA 2\nAAAA 3", "AAAA -1"):
            self.path.write_text(text)
            with self.assertRaises(ValueError):
                QuadgramScorer(self.path)

    def test_controls_reexecute_identical_search_and_budget(self):
        models = [Model("p27", 27, tuple(range(97)))]
        options = {"max_per_model": 5, "max_total": 5, "top": 2}
        result = matched_controls(K4_CIPHERTEXT, models, self.scorer, repetitions=3, seed=97, **options)
        again = matched_controls(K4_CIPHERTEXT, models, self.scorer, repetitions=3, seed=97, **options)
        self.assertEqual(result, again)
        self.assertFalse(result["all_searches_complete"])
        for control in result["controls"]:
            if control["kind"] == "histogram_shuffle":
                self.assertEqual(Counter(control["ciphertext"]), Counter(K4_CIPHERTEXT))
            manual = search(control["ciphertext"], models, self.scorer, **options)
            self.assertEqual(control["best_unknown_only_score"], manual["best_unknown_only_score"])
            self.assertEqual(control["evaluated_completions"], 5)


class DiagnosticsAndLedgerTests(unittest.TestCase):
    def test_observed_diagnostics(self):
        self.assertEqual(crib_parity()["pair_matches"], 13)
        self.assertEqual(crib_parity()["independent_equalities"], 11)
        self.assertEqual(width_bigrams()["duplicate_excess"], 11)
        self.assertEqual(K4_CIPHERTEXT[55:64], "DIAWINFBN")

    def test_cli_emits_schema_valid_provenance(self):
        output = io.StringIO()
        with redirect_stdout(output):
            main(["diagnostics"])
        result = json.loads(output.getvalue())
        schema = json.loads(Path("docs/EXPERIMENT_SCHEMA.json").read_text())
        jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(result)
        self.assertEqual(result["code_sha256"], source_hash())
        self.assertFalse(result["is_solution"])
        self.assertEqual(result["result"]["models_checked"], 180)

    def test_new_ledger_entries_have_narrow_scopes_and_evidence(self):
        ledger = json.loads(Path("docs/HYPOTHESIS_LEDGER.json").read_text())
        schema = json.loads(Path("docs/HYPOTHESIS_SCHEMA.json").read_text())
        jsonschema.validate(ledger, schema)
        for row in ledger["hypotheses"]:
            if row["status"] == "eliminated":
                self.assertIn(row["evidence_type"], ("exact_conflict", "exhaustive_bounded"))
                self.assertTrue(row["positive_controls"])
            for path in row["evidence_files"]:
                self.assertTrue(Path(path).is_file(), path)


if __name__ == "__main__":
    unittest.main()

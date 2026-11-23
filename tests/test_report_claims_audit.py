"""Cross-check the earlier independent audit against the current workbench."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from kryptos.constants import FIXTURES, K4_CIPHERTEXT, KRYPTOS, STD
from kryptos.primitives import MODES
from kryptos.solver import Model, decrypt, infer_key
from research import verify_report_claims as audit


class ReportAuditTests(unittest.TestCase):
    def test_original_script_snapshot_is_byte_exact(self):
        data = Path("docs/archive/legacy_kryptos_analysis.py").read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), FIXTURES["source_sha256"])

    def test_independent_period_checker_agrees_with_workbench(self):
        for alphabet in (STD, KRYPTOS):
            for mode, old_mode in zip(MODES, ("vig", "beau", "vbeau")):
                rows = audit.period_check(K4_CIPHERTEXT, alphabet, alphabet, old_mode)["period_checks"]
                for row in rows:
                    model = Model("cross-check", row["period"], tuple(range(97)), alphabet, mode)
                    result = infer_key(K4_CIPHERTEXT, model)
                    self.assertEqual(result["compatible"], row["compatible"])
                    self.assertEqual(result["distinct_anchor_residues"], row["distinct_anchor_residues"])

    def test_independent_sparse_collision_example_recovers_exactly(self):
        case = audit.synthetic_collision_counterexample()
        cuts = case["fixed_partition_boundaries"]
        blocks = [range(a, b) for a, b in zip(cuts, cuts[1:])]
        route = tuple(i for b in case["block_order_zero_based"] for i in blocks[b])
        model = Model("cross-check", 24, route, order="T_S")
        fit = infer_key(case["ciphertext"], model)
        self.assertTrue(fit["compatible"])
        self.assertEqual(fit["consistency_checks"], 0)
        self.assertEqual(decrypt(case["ciphertext"], fit["key"], model), case["plaintext"])

    def test_first_audit_reproduces_published_json(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "checked.json"
            subprocess.run([sys.executable, "-m", "research.verify_report_claims", "--output", str(output)],
                           capture_output=True, text=True, check=True)
            actual = json.loads(output.read_text())
        expected = json.loads(Path("out/november_20261123/independently_checked.json").read_text())
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()

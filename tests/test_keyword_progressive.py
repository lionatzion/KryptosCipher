"""Independent enumeration and planted controls for the progressive-key filter."""
import random
import unittest

import numpy as np

from research import keyword_progressive as kp
from research.opus_review.core import CRIB_POSITIONS


class ProgressiveKeywordTests(unittest.TestCase):
    def test_filter_matches_all_drift_scalar_enumeration(self):
        rng = random.Random(91)
        observed = np.array([[rng.randrange(26) for _ in CRIB_POSITIONS]
                             for _ in range(20)], dtype=np.int16)
        # Include actual positive instances, including the noninvertible gap cases.
        for period in kp.PERIODS:
            for drift in (0, 1, 13, 25):
                base = [rng.randrange(26) for _ in range(period)]
                planted = np.array([[kp.schedule(base, drift, 97)[i]
                                     for i in CRIB_POSITIONS]], dtype=np.int16)
                batch = np.concatenate((observed, planted))
                self.assertEqual(sorted(kp.progressive_survivors(batch, period)),
                                 sorted(kp.scalar_survivors(batch, period)))
                self.assertIn((len(batch) - 1, drift), kp.progressive_survivors(batch, period))

    def test_phase_changes_are_absorbed_in_free_base(self):
        rng = random.Random(13)
        for period in kp.PERIODS:
            base = [rng.randrange(26) for _ in range(period)]
            drift = rng.randrange(26)
            for phase in range(period):
                self.assertEqual(kp.schedule(base, drift, 97, phase),
                                 kp.schedule(kp.phase_zero_base(base, drift, phase), drift, 97))

    def test_tampering_rejects_original_parameters(self):
        for period in kp.PERIODS:
            base = [(5 * r + 7) % 26 for r in range(period)]
            drift = 9
            values = np.array([[kp.schedule(base, drift, 97)[i]
                                for i in CRIB_POSITIONS]], dtype=np.int16)
            self.assertIn((0, drift), kp.progressive_survivors(values, period))
            changed = values.copy()
            changed[0, kp.repeat_pairs(period)[0][0]] ^= 1
            self.assertNotIn((0, drift), kp.progressive_survivors(changed, period))


if __name__ == "__main__":
    unittest.main()

"""
Unit Test Suite: DPD Roll Rates & Transition Matrix
===================================================
Validates transition probability row sums, cure rates, and roll hazards.
"""

import unittest
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.roll_rate_engine import RollRateEngine

class TestRollRateEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = RollRateEngine('data/dpd_snapshot_history.csv')
        cls.matrix_data = cls.engine.compute_transition_matrix()
        cls.rates = cls.engine.compute_cure_and_roll_rates()

    def test_transition_probability_sums(self):
        mat = self.matrix_data['probability_matrix']
        for b_from, targets in mat.items():
            tot_p = sum(targets.values())
            # For buckets with historical observations, row probabilities sum to 1.0
            if self.matrix_data['prior_totals_count'][b_from] > 0:
                self.assertAlmostEqual(tot_p, 1.0, places=4, msg=f"Row {b_from} sum != 1.0")

    def test_current_stay_stability(self):
        stay_p = self.rates['Stay_Current_Rate']
        self.assertGreater(stay_p, 0.90) # Over 90% stability
        self.assertAlmostEqual(stay_p, 0.9325, places=2)

    def test_roll_hazard(self):
        roll_30_60 = self.rates['Roll_Rate_30_to_60']
        self.assertGreater(roll_30_60, 0.40) # Elevated roll rate
        self.assertAlmostEqual(roll_30_60, 0.5231, places=2)

if __name__ == '__main__':
    unittest.main()

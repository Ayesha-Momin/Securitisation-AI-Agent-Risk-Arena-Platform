"""
Unit Test Suite: DAX Measures Engine
====================================
Validates all core portfolio balance, weighted average, and delinquency calculations.
"""

import unittest
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.dax_measures import SecuritisationDAXEngine

class TestDAXMeasuresEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = SecuritisationDAXEngine(
            'data/auto_loan_securitisation_data.csv',
            'data/dpd_snapshot_history.csv',
            'data/dynamic_loss_monthly.csv'
        )

    def test_total_portfolio_balances(self):
        curr_bal = self.engine.total_current_balance()
        orig_bal = self.engine.total_original_balance()
        self.assertAlmostEqual(curr_bal, 317785202.14, places=2)
        self.assertAlmostEqual(orig_bal, 546073700.00, places=2)
        self.assertGreater(orig_bal, curr_bal)

    def test_pool_factor(self):
        pf = self.engine.pool_factor()
        self.assertAlmostEqual(pf, 0.5819, places=3)
        self.assertTrue(0.0 < pf < 1.0)

    def test_loan_counts(self):
        self.assertEqual(self.engine.total_loan_count(), 500)
        self.assertEqual(self.engine.active_loan_count(), 476)
        self.assertEqual(self.engine.defaulted_loan_count(), 9)

    def test_weighted_averages(self):
        wac = self.engine.weighted_average_coupon()
        wam = self.engine.weighted_average_maturity()
        wala = self.engine.weighted_average_loan_age()
        ltv = self.engine.weighted_average_current_ltv()
        
        self.assertAlmostEqual(wac, 10.95, places=1)
        self.assertAlmostEqual(wam, 45.14, places=1)
        self.assertAlmostEqual(wala, 16.76, places=1)
        self.assertTrue(0.5 < ltv < 0.8)

    def test_delinquency_metrics(self):
        d30 = self.engine.delinquency_rate_30plus()
        d60 = self.engine.serious_delinquency_rate_60plus()
        d90 = self.engine.critical_delinquency_rate_90plus()
        
        self.assertGreater(d30, d60)
        self.assertGreater(d60, d90)
        self.assertAlmostEqual(d30, 0.1411, places=2)
        self.assertAlmostEqual(d60, 0.1059, places=2)

    def test_concentration_and_hhi(self):
        hhi = self.engine.state_hhi()
        top10 = self.engine.top_n_borrower_concentration(10)
        
        # Well diversified portfolio has HHI < 1500
        self.assertLess(hhi, 1500.0)
        self.assertLess(top10['Top10ConcentrationPct'], 0.15)

if __name__ == '__main__':
    unittest.main()

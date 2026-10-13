"""
Unit Test Suite: Waterfall & Tranche Engine
===========================================
Validates cash flow conservation, sequential amortization priority,
credit enhancement accretion, and trigger monitoring.
"""

import unittest
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.waterfall_engine import WaterfallEngine

class TestWaterfallEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = WaterfallEngine()
        cls.results = cls.engine.simulate_12_months('data/dynamic_loss_monthly.csv')

    def test_simulation_duration(self):
        self.assertEqual(len(self.results), 12)

    def test_senior_amortisation_and_credit_enhancement(self):
        m1 = self.results[0]
        m12 = self.results[-1]
        
        # Senior balance amortizes down over time
        self.assertLess(m12['Senior_Ending_Balance'], m1['Senior_Ending_Balance'])
        
        # Senior credit enhancement % increases over time due to sequential de-leveraging
        self.assertGreater(m12['Senior_CreditEnhancement_Pct'], m1['Senior_CreditEnhancement_Pct'])
        self.assertGreater(m12['Senior_CreditEnhancement_Pct'], 20.0)

    def test_cash_flow_conservation(self):
        for r in self.results:
            total_distributed = (
                r['ServicingFees'] +
                r['Senior_Interest_Paid'] +
                r['Mezzanine_Interest_Paid'] +
                r['Senior_Principal_Paid'] +
                r['Mezzanine_Principal_Paid'] +
                r['Equity_Residual_Paid']
            )
            # Total distributed must not exceed gross collections plus reserve draws
            self.assertLessEqual(total_distributed, r['GrossCollections'] + 1000.0)

    def test_loss_trigger_status(self):
        for r in self.results:
            # Baseline portfolio losses remain below 3.0% trigger
            self.assertFalse(r['Loss_Trigger_Breached'])

if __name__ == '__main__':
    unittest.main()

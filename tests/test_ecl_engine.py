"""
Unit Test Suite: IFRS 9 ECL Model Engine
========================================
Validates Stage 1, 2, and 3 classifications, provision amounts,
and mathematical reconciliation against the Excel model (0.00% variance).
"""

import unittest
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.ecl_model import IFRS9ECLModel

class TestIFRS9ECLEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = IFRS9ECLModel('data/auto_loan_securitisation_data.csv')

    def test_baseline_ecl_reconciliation(self):
        res = self.model.baseline_metrics()
        
        # Verify exact portfolio balance
        self.assertAlmostEqual(res['Total_Balance'], 317785202.14, places=2)
        
        # Verify baseline total ECL provision
        self.assertAlmostEqual(res['Total_ECL_Provision'], 11662952.90, places=2)
        
        # Verify portfolio coverage ratio
        self.assertAlmostEqual(res['Portfolio_Coverage_Ratio'], 0.0367, places=3)

    def test_stage_distribution(self):
        res = self.model.baseline_metrics()
        stg1 = res['Stages']['Stage_1']
        stg2 = res['Stages']['Stage_2']
        stg3 = res['Stages']['Stage_3']
        
        # Total counts must equal 500
        self.assertEqual(stg1['Count'] + stg2['Count'] + stg3['Count'], 500)
        self.assertEqual(stg1['Count'], 422)
        self.assertEqual(stg2['Count'], 45)
        self.assertEqual(stg3['Count'], 33)
        
        # Staging provisions
        self.assertAlmostEqual(stg1['ECL_Provision'], 2792098.27, places=2)
        self.assertAlmostEqual(stg2['ECL_Provision'], 1648395.03, places=2)
        self.assertAlmostEqual(stg3['ECL_Provision'], 7222459.60, places=2)
        
        # Coverage ascending by stage severity
        self.assertLess(stg1['Coverage_Ratio'], stg2['Coverage_Ratio'])
        self.assertLess(stg2['Coverage_Ratio'], stg3['Coverage_Ratio'])

    def test_stress_sensitivity(self):
        # Moderate stress (1.5x PD, 10% LGD haircut)
        res_stress = self.model.compute_ecl_portfolio(pd_multiplier=1.5, lgd_haircut=0.10)
        res_base = self.model.compute_ecl_portfolio(pd_multiplier=1.0, lgd_haircut=0.0)
        
        self.assertGreater(res_stress['Total_ECL_Provision'], res_base['Total_ECL_Provision'])
        self.assertGreater(res_stress['Portfolio_Coverage_Ratio'], res_base['Portfolio_Coverage_Ratio'])

if __name__ == '__main__':
    unittest.main()

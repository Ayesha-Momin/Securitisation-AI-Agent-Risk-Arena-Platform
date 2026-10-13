"""
Macroeconomic Stress Testing & What-If Engine
=============================================
Pure Python reference implementation simulating 4 standardized stress scenarios:
  1. Base Case (Current economic conditions)
  2. Moderate Stress (Mild economic slowdown, 1.5x PD, 10% LGD increase)
  3. Severe Stress (Significant recession, 2.5x PD, 25% LGD increase)
  4. Crisis Mode (2008 GFC / IL&FS shock, 4.0x PD, 40% LGD increase)
Evaluates stressed ECL provisions, tranche impairment, and waterfall trigger breaches.
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Dict, Any, List
from models.ecl_model import IFRS9ECLModel
from models.dax_measures import SecuritisationDAXEngine

class StressTestingEngine:
    def __init__(self, loan_csv_path: str):
        self.loan_path = loan_csv_path
        self.ecl_model = IFRS9ECLModel(loan_csv_path)
        self.dax_engine = SecuritisationDAXEngine(loan_csv_path)

    def run_all_scenarios(self) -> Dict[str, Any]:
        pool_balance = self.dax_engine.total_current_balance()
        scenarios = {
            'Base Case': {
                'pd_mult': 1.0,
                'lgd_haircut': 0.0,
                'cpr': 0.15,
                'description': 'Current baseline economic performance'
            },
            'Moderate Stress': {
                'pd_mult': 1.5,
                'lgd_haircut': 0.10,
                'cpr': 0.12,
                'description': 'Mild slowdown, rising interest rates, lower prepayment'
            },
            'Severe Stress': {
                'pd_mult': 2.5,
                'lgd_haircut': 0.25,
                'cpr': 0.08,
                'description': 'Significant recession, automotive market contraction'
            },
            'Crisis Mode (2008/IL&FS)': {
                'pd_mult': 4.0,
                'lgd_haircut': 0.40,
                'cpr': 0.04,
                'description': 'Systemic financial crisis, sharp collateral deflation'
            }
        }

        results = {}
        for name, params in scenarios.items():
            ecl_res = self.ecl_model.compute_ecl_portfolio(
                pd_multiplier=params['pd_mult'],
                lgd_haircut=params['lgd_haircut']
            )
            
            tot_ecl = ecl_res['Total_ECL_Provision']
            cov = ecl_res['Portfolio_Coverage_Ratio']
            
            # Tranche protection analysis
            # Senior = 85% (INR 270.1M), Mezzanine = 10% (INR 31.8M), Equity = 5% (INR 15.9M)
            # Reserve = 2% (INR 6.35M), OC = 3% (INR 9.53M)
            # Total First-Loss Protection for Senior = 10% + 5% + 2% + 3% = 20% (INR 63.56M)
            first_loss_capacity = pool_balance * 0.20
            mezzanine_first_loss = pool_balance * 0.10 # Equity + Reserve + OC
            
            senior_impaired = tot_ecl > first_loss_capacity
            mezz_impaired = tot_ecl > mezzanine_first_loss
            
            results[name] = {
                'Description': params['description'],
                'PD_Multiplier': params['pd_mult'],
                'LGD_Haircut': params['lgd_haircut'],
                'CPR_Annualised': params['cpr'],
                'Stressed_ECL_Provision': tot_ecl,
                'ECL_Coverage_Ratio': cov,
                'First_Loss_Capacity': first_loss_capacity,
                'Loss_Buffer_Remaining': max(0.0, first_loss_capacity - tot_ecl),
                'Class_A_Senior_Impaired': senior_impaired,
                'Class_B_Mezzanine_Impaired': mezz_impaired,
                'Trigger_Breach_Expected': (tot_ecl / pool_balance) > 0.05
            }

        return results

if __name__ == '__main__':
    engine = StressTestingEngine('data/auto_loan_securitisation_data.csv')
    res = engine.run_all_scenarios()
    print("Stress Testing Multi-Scenario Analysis:")
    for scn, data in res.items():
        print(f"\n--- {scn} ---")
        print(f"  Stressed ECL: INR {data['Stressed_ECL_Provision']:,.2f}")
        print(f"  Coverage Ratio: {data['ECL_Coverage_Ratio']*100:.2f}%")
        print(f"  Loss Buffer Remaining: INR {data['Loss_Buffer_Remaining']:,.2f}")
        print(f"  Senior Impaired: {data['Class_A_Senior_Impaired']}")
        print(f"  Trigger Breach: {data['Trigger_Breach_Expected']}")

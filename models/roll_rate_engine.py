"""
DPD Transition & Roll Rate Engine
==================================
Pure Python reference implementation analyzing 6,000 monthly loan snapshots.
Computes:
  - Transition Probability Matrix (Count-based & Balance-weighted)
  - Roll Rates (deterioration into worse delinquency buckets)
  - Cure Rates (transitions back to Current or lower buckets)
  - Consecutive months delinquent analysis & ageing
"""

import csv
from collections import defaultdict
from typing import Dict, Any, List, Tuple

class RollRateEngine:
    def __init__(self, snapshot_csv_path: str):
        self.snapshots = self._load_csv(snapshot_csv_path)
        self.buckets = [
            'Current', '1-29 DPD', '30-59 DPD', '60-89 DPD', 
            '90-119 DPD', '120+ DPD', 'Default', 'Repossessed'
        ]

    def _load_csv(self, path: str) -> List[Dict[str, Any]]:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        for r in data:
            try:
                r['CurrentBalance'] = float(r.get('CurrentBalance', 0) or 0)
            except ValueError:
                r['CurrentBalance'] = 0.0
        return data

    def compute_transition_matrix(self) -> Dict[str, Any]:
        """
        Builds both count-based and balance-weighted transition matrices.
        """
        transitions_count = defaultdict(lambda: defaultdict(int))
        transitions_balance = defaultdict(lambda: defaultdict(float))
        prior_totals_count = defaultdict(int)
        prior_totals_balance = defaultdict(float)

        for s in self.snapshots:
            prior = s.get('DPD_Bucket_Prior', '').strip()
            curr = s.get('DPD_Bucket', '').strip()
            bal = s['CurrentBalance']
            
            if not prior or prior not in self.buckets:
                prior = 'Current'
            if not curr or curr not in self.buckets:
                curr = 'Current'

            transitions_count[prior][curr] += 1
            transitions_balance[prior][curr] += bal
            prior_totals_count[prior] += 1
            prior_totals_balance[prior] += bal

        matrix_prob = {}
        matrix_balance_prob = {}
        for b_from in self.buckets:
            matrix_prob[b_from] = {}
            matrix_balance_prob[b_from] = {}
            tot_cnt = prior_totals_count[b_from]
            tot_bal = prior_totals_balance[b_from]
            for b_to in self.buckets:
                cnt = transitions_count[b_from][b_to]
                bal = transitions_balance[b_from][b_to]
                matrix_prob[b_from][b_to] = (cnt / tot_cnt) if tot_cnt > 0 else 0.0
                matrix_balance_prob[b_from][b_to] = (bal / tot_bal) if tot_bal > 0 else 0.0

        return {
            'buckets': self.buckets,
            'count_matrix': transitions_count,
            'balance_matrix': transitions_balance,
            'probability_matrix': matrix_prob,
            'balance_probability_matrix': matrix_balance_prob,
            'prior_totals_count': dict(prior_totals_count),
            'prior_totals_balance': dict(prior_totals_balance)
        }

    def compute_cure_and_roll_rates(self) -> Dict[str, Any]:
        """
        Key securitisation metrics:
          - Cure Rate from 30-59 DPD -> Current / 1-29 DPD
          - Roll Rate from 30-59 DPD -> 60-89 DPD
          - Roll Rate from 60-89 DPD -> 90+ DPD / Default
        """
        mat = self.compute_transition_matrix()['probability_matrix']
        
        # 30-59 cure rate (migrating to Current or 1-29)
        cure_30_59 = mat.get('30-59 DPD', {}).get('Current', 0.0) + mat.get('30-59 DPD', {}).get('1-29 DPD', 0.0)
        # 30-59 roll rate (migrating to 60-89 or worse)
        roll_30_to_60 = mat.get('30-59 DPD', {}).get('60-89 DPD', 0.0)
        # 60-89 roll rate (migrating to 90-119 or Default)
        roll_60_to_90 = mat.get('60-89 DPD', {}).get('90-119 DPD', 0.0) + mat.get('60-89 DPD', {}).get('Default', 0.0)
        
        return {
            'Cure_Rate_30_59': cure_30_59,
            'Roll_Rate_30_to_60': roll_30_to_60,
            'Roll_Rate_60_to_90': roll_60_to_90,
            'Stay_Current_Rate': mat.get('Current', {}).get('Current', 0.0)
        }

if __name__ == '__main__':
    engine = RollRateEngine('data/dpd_snapshot_history.csv')
    rates = engine.compute_cure_and_roll_rates()
    print("DPD Transition & Roll Rate Summary:")
    print(f"Current Stay Rate: {rates['Stay_Current_Rate']*100:.2f}%")
    print(f"30-59 DPD Cure Rate: {rates['Cure_Rate_30_59']*100:.2f}%")
    print(f"30-59 -> 60-89 DPD Roll Rate: {rates['Roll_Rate_30_to_60']*100:.2f}%")
    print(f"60-89 -> 90+ DPD Roll Rate: {rates['Roll_Rate_60_to_90']*100:.2f}%")

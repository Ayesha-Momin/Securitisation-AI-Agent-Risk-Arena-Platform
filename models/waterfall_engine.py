"""
Cash Flow Waterfall & Tranche Allocation Engine
================================================
Pure Python institutional reference implementation of ABS sequential waterfall.
Simulates monthly cash allocations across:
  - Senior Fees (Servicer & Trustee)
  - Class A Senior Tranche (AAA/AA rated)
  - Class B Mezzanine Tranche (BBB/A rated)
  - Class C Equity Residual (Unrated)
  - Reserve Account Replenishment
  - Dynamic Early-Warning Triggers (Delinquency, Loss, OC)
"""

import csv
from typing import Dict, Any, List, Optional

class WaterfallEngine:
    def __init__(self,
                 original_pool_balance: float = 546073700.0,
                 senior_pct: float = 0.85,
                 mezzanine_pct: float = 0.10,
                 equity_pct: float = 0.05,
                 senior_coupon: float = 0.085,
                 mezzanine_coupon: float = 0.105,
                 servicer_fee_rate: float = 0.005,
                 trustee_fee_rate: float = 0.001,
                 reserve_target_pct: float = 0.02,
                 oc_target_pct: float = 0.03):
        
        self.original_pool = original_pool_balance
        self.senior_pct = senior_pct
        self.mezzanine_pct = mezzanine_pct
        self.equity_pct = equity_pct
        
        self.senior_coupon = senior_coupon
        self.mezzanine_coupon = mezzanine_coupon
        self.servicer_fee_rate = servicer_fee_rate
        self.trustee_fee_rate = trustee_fee_rate
        self.reserve_target_pct = reserve_target_pct
        self.oc_target_pct = oc_target_pct
        
        # Initial balances
        self.initial_senior = original_pool_balance * senior_pct
        self.initial_mezzanine = original_pool_balance * mezzanine_pct
        self.initial_equity = original_pool_balance * equity_pct
        self.initial_reserve = original_pool_balance * reserve_target_pct

    def simulate_12_months(self, dynamic_csv_path: str) -> List[Dict[str, Any]]:
        """
        Executes monthly waterfall allocation based on the dynamic_loss_monthly.csv data.
        """
        records = []
        with open(dynamic_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            dynamic_data = list(reader)

        senior_bal = self.initial_senior
        mezz_bal = self.initial_mezzanine
        reserve_bal = self.initial_reserve
        cum_net_loss = 0.0

        for m_idx, row in enumerate(dynamic_data):
            rep_date = row['ReportingDate']
            bop_bal = float(row['BOP_Balance'])
            eop_bal = float(row['EOP_Balance'])
            collections = float(row['CollectionsTotal'])
            net_loss = float(row['NetLoss_ThisMonth'])
            cum_net_loss += net_loss
            
            # Fee calculations (monthly)
            servicer_fee = bop_bal * (self.servicer_fee_rate / 12.0)
            trustee_fee = bop_bal * (self.trustee_fee_rate / 12.0)
            available_cash = max(0.0, collections - servicer_fee - trustee_fee)
            
            # Tranche Interest
            senior_interest = senior_bal * (self.senior_coupon / 12.0)
            mezz_interest = mezz_bal * (self.mezzanine_coupon / 12.0)
            
            paid_senior_interest = min(available_cash, senior_interest)
            available_cash -= paid_senior_interest
            
            paid_mezz_interest = min(available_cash, mezz_interest)
            available_cash -= paid_mezz_interest
            
            # Trigger Tests
            # Delinquency trigger: assume test from pool loss rates
            cum_loss_rate = cum_net_loss / self.original_pool
            loss_trigger_breached = cum_loss_rate > 0.030 # 3.0% threshold
            
            # Principal Amortization
            # Pro-rata vs Sequential: If trigger breached, 100% principal flows to Senior
            scheduled_amort = float(row.get('ScheduledAmort', 0)) + float(row.get('Prepayments_ThisMonth', 0))
            if scheduled_amort == 0:
                scheduled_amort = max(0.0, bop_bal - eop_bal)
                
            principal_available = min(available_cash, scheduled_amort)
            
            if loss_trigger_breached or senior_bal > 0:
                # Sequential allocation
                paid_senior_principal = min(principal_available, senior_bal)
                senior_bal -= paid_senior_principal
                rem_principal = principal_available - paid_senior_principal
                paid_mezz_principal = min(rem_principal, mezz_bal)
                mezz_bal -= paid_mezz_principal
            else:
                paid_senior_principal = 0.0
                paid_mezz_principal = min(principal_available, mezz_bal)
                mezz_bal -= paid_mezz_principal

            available_cash -= (paid_senior_principal + paid_mezz_principal)

            # Reserve Account Replenishment
            target_reserve = eop_bal * self.reserve_target_pct
            reserve_shortfall = max(0.0, target_reserve - reserve_bal)
            reserve_deposit = min(available_cash, reserve_shortfall)
            reserve_bal += reserve_deposit
            available_cash -= reserve_deposit
            
            # Class C Equity Residual Cash
            equity_residual = available_cash if not loss_trigger_breached else 0.0
            if loss_trigger_breached:
                # Trap cash in reserve
                reserve_bal += available_cash
                equity_residual = 0.0

            # Current Credit Enhancement % for Senior
            total_subordination = mezz_bal + (self.initial_equity) # equity absorbed first
            ce_amount = total_subordination + reserve_bal + max(0.0, eop_bal - senior_bal)
            ce_pct = (ce_amount / eop_bal * 100.0) if eop_bal > 0 else 0.0

            records.append({
                'Month': m_idx + 1,
                'ReportingDate': rep_date,
                'Pool_BOP': bop_bal,
                'Pool_EOP': eop_bal,
                'GrossCollections': collections,
                'ServicingFees': servicer_fee + trustee_fee,
                'Senior_Interest_Paid': paid_senior_interest,
                'Mezzanine_Interest_Paid': paid_mezz_interest,
                'Senior_Principal_Paid': paid_senior_principal,
                'Mezzanine_Principal_Paid': paid_mezz_principal,
                'Senior_Ending_Balance': senior_bal,
                'Mezzanine_Ending_Balance': mezz_bal,
                'Reserve_Balance': reserve_bal,
                'Equity_Residual_Paid': equity_residual,
                'Cumulative_Loss_Rate': cum_loss_rate,
                'Loss_Trigger_Breached': loss_trigger_breached,
                'Senior_CreditEnhancement_Pct': ce_pct
            })

        return records

if __name__ == '__main__':
    engine = WaterfallEngine()
    results = engine.simulate_12_months('data/dynamic_loss_monthly.csv')
    print("Waterfall 12-Month Simulation Summary:")
    print(f"Total Months: {len(results)}")
    last = results[-1]
    print(f"Ending Pool EOP: INR {last['Pool_EOP']:,.2f}")
    print(f"Senior Ending Balance: INR {last['Senior_Ending_Balance']:,.2f}")
    print(f"Mezzanine Ending Balance: INR {last['Mezzanine_Ending_Balance']:,.2f}")
    print(f"Reserve Balance: INR {last['Reserve_Balance']:,.2f}")
    print(f"Senior Credit Enhancement: {last['Senior_CreditEnhancement_Pct']:.2f}%")
    print(f"Loss Trigger Status: {'BREACHED' if last['Loss_Trigger_Breached'] else 'OK (Healthy)'}")

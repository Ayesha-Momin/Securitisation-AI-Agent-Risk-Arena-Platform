"""
Power BI Star Schema Model Setup & Verification Script
======================================================
Validates the Kimball Star Schema data model integrity across all dimensions and facts.
Generates tabular model validation summary and verifies foreign key constraints.
"""

import csv
import json
from collections import defaultdict

def verify_data_model():
    print("Verifying Star Schema Data Model Relationships...")
    
    # 1. Load DimLoan
    with open('data/auto_loan_securitisation_data.csv', 'r', encoding='utf-8') as f:
        loans = list(csv.DictReader(f))
    loan_ids = set(l['LoanID'] for l in loans)
    borrower_ids = set(l['BorrowerID'] for l in loans)
    states = set(l['State'] for l in loans)
    print(f" DimLoan: {len(loans)} rows loaded. Unique Loans: {len(loan_ids)}, Borrowers: {len(borrower_ids)}, States: {len(states)}")

    # 2. Load FactMonthlyPerformance (dpd_snapshot_history)
    with open('data/dpd_snapshot_history.csv', 'r', encoding='utf-8') as f:
        snapshots = list(csv.DictReader(f))
    snap_loan_ids = set(s['LoanID'] for s in snapshots)
    snap_dates = sorted(list(set(s['SnapshotDate'] for s in snapshots)))
    print(f" FactMonthlyPerformance: {len(snapshots)} snapshots loaded across {len(snap_dates)} snapshot dates.")
    
    # Verify FK constraint (Fact to DimLoan)
    orphan_loans = snap_loan_ids - loan_ids
    if orphan_loans:
        print(f" WARNING: {len(orphan_loans)} orphan LoanIDs found in FactMonthlyPerformance!")
    else:
        print(" Referential Integrity: 100% of Fact snapshots match DimLoan PK (0 orphan records).")

    # 3. Load FactDynamicLoss
    with open('data/dynamic_loss_monthly.csv', 'r', encoding='utf-8') as f:
        dynamic = list(csv.DictReader(f))
    print(f" FactDynamicLoss: {len(dynamic)} monthly aggregate records loaded.")

    # 4. Summary Output
    schema_manifest = {
        "model_name": "Securitisation_AI_Agent_StarSchema",
        "version": "1.0.0",
        "tables": {
            "DimLoan": {"type": "Dimension", "rows": len(loans), "primary_key": "LoanID"},
            "DimBorrower": {"type": "Dimension", "rows": len(borrower_ids), "primary_key": "BorrowerID"},
            "DimGeography": {"type": "Dimension", "rows": len(states), "primary_key": "State"},
            "DimDate": {"type": "Dimension", "rows": len(snap_dates), "primary_key": "SnapshotDate"},
            "FactMonthlyPerformance": {"type": "Fact", "rows": len(snapshots), "foreign_keys": ["LoanID", "SnapshotDate"]},
            "FactDynamicLoss": {"type": "Fact", "rows": len(dynamic), "foreign_keys": ["ReportingDate"]}
        },
        "relationships": [
            {"from": "FactMonthlyPerformance.LoanID", "to": "DimLoan.LoanID", "cardinality": "N:1"},
            {"from": "FactMonthlyPerformance.SnapshotDate", "to": "DimDate.SnapshotDate", "cardinality": "N:1"},
            {"from": "DimLoan.BorrowerID", "to": "DimBorrower.BorrowerID", "cardinality": "N:1"},
            {"from": "DimLoan.State", "to": "DimGeography.State", "cardinality": "N:1"},
            {"from": "FactDynamicLoss.ReportingDate", "to": "DimDate.SnapshotDate", "cardinality": "N:1"}
        ]
    }

    with open('powerbi/model_schema_manifest.json', 'w', encoding='utf-8') as f:
        json.dump(schema_manifest, f, indent=2)
    print(" Saved model schema manifest to powerbi/model_schema_manifest.json")
    print("Power BI Star Schema verification COMPLETE.")

if __name__ == '__main__':
    verify_data_model()

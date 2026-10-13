"""
Securitisation Analytics & Arena Web Server
============================================
Lightweight, pure Python high-performance web server powering the
interactive Securitisation Risk Arena & Power BI Analytics Platform.
Zero external C/binary dependencies - 100% resilient across any OS environment.
"""

import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.dax_measures import SecuritisationDAXEngine
from models.ecl_model import IFRS9ECLModel
from models.waterfall_engine import WaterfallEngine
from models.roll_rate_engine import RollRateEngine
from models.stress_testing import StressTestingEngine

# Pre-load analytical engines
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
LOAN_CSV = os.path.join(DATA_DIR, 'auto_loan_securitisation_data.csv')
SNAP_CSV = os.path.join(DATA_DIR, 'dpd_snapshot_history.csv')
DYN_CSV = os.path.join(DATA_DIR, 'dynamic_loss_monthly.csv')

dax_engine = SecuritisationDAXEngine(LOAN_CSV, SNAP_CSV, DYN_CSV)
ecl_model = IFRS9ECLModel(LOAN_CSV)
waterfall_engine = WaterfallEngine()
roll_engine = RollRateEngine(SNAP_CSV)
stress_engine = StressTestingEngine(LOAN_CSV)

class SecuritisationAPIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        super().__init__(*args, directory=static_dir, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path.startswith('/api/'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            data = {}
            if path == '/api/summary':
                data = dax_engine.generate_full_metrics_summary()
            elif path == '/api/ecl':
                data = ecl_model.baseline_metrics()
            elif path == '/api/waterfall':
                data = waterfall_engine.simulate_12_months(DYN_CSV)
            elif path == '/api/rollrates':
                trans = roll_engine.compute_transition_matrix()
                rates = roll_engine.compute_cure_and_roll_rates()
                data = {
                    'buckets': trans['buckets'],
                    'probability_matrix': trans['probability_matrix'],
                    'balance_probability_matrix': trans['balance_probability_matrix'],
                    'rates': rates
                }
            elif path == '/api/dynamic':
                data = dax_engine.dynamic_loss_metrics()
            elif path == '/api/stress':
                pd_mult = float(query.get('pd_multiplier', [1.0])[0])
                lgd_cut = float(query.get('lgd_haircut', [0.0])[0])
                custom_ecl = ecl_model.compute_ecl_portfolio(pd_multiplier=pd_mult, lgd_haircut=lgd_cut)
                all_scenarios = stress_engine.run_all_scenarios()
                data = {
                    'custom_run': custom_ecl,
                    'standard_scenarios': all_scenarios
                }
            elif path == '/api/buckets':
                data = dax_engine.dpd_bucket_breakdown()
            elif path == '/api/arena':
                data = {
                    "player": {
                        "name": "Data Analyst Fellow",
                        "title": "Lead Structured Finance Analyst",
                        "level": 5,
                        "xp": 7250,
                        "next_level_xp": 15000,
                        "rank": "Lead Analyst"
                    },
                    "score_card": {
                        "dax_accuracy": 290,
                        "query_performance": 145,
                        "waterfall_tranche": 195,
                        "ifrs9_ecl": 150,
                        "investor_reporting": 100,
                        "dashboard_insight": 95,
                        "total_score": 975,
                        "max_score": 1000
                    },
                    "levels": [
                        {"id": 1, "title": "Data Foundation", "status": "Completed", "score": "100/100", "desc": "Single auto loan pool; filter context and basic aggregations."},
                        {"id": 2, "title": "Time Intelligence", "status": "Completed", "score": "98/100", "desc": "YTD, QTD, MTD, rolling averages, and date relationships."},
                        {"id": 3, "title": "Iterator Mastery", "status": "Completed", "score": "97/100", "desc": "Weighted averages using SUMX and concentration with TOPN/RANKX."},
                        {"id": 4, "title": "Virtual Tables", "status": "Completed", "score": "95/100", "desc": "SUMMARIZE, ADDCOLUMNS, dynamic stratification tables."},
                        {"id": 5, "title": "Waterfall Wizard", "status": "Completed", "score": "100/100", "desc": "Sequential cash flow waterfall, trigger testing, and credit enhancement."},
                        {"id": 6, "title": "IFRS 9 ECL Framework", "status": "Completed", "score": "100/100", "desc": "Staging classification, PD/LGD/EAD models matching Excel within 0.01%."},
                        {"id": 7, "title": "Rating Agency Reporting", "status": "Completed", "score": "95/100", "desc": "Loan-level data tape generation for S&P, Moody's, and CRISIL."},
                        {"id": 8, "title": "Crisis Mode (Level 8)", "status": "Unlocked", "score": "In Progress", "desc": "Simulated systemic liquidity freeze and vintage deterioration under severe time pressure."}
                    ],
                    "badges": [
                        {"title": "DAX Master", "icon": "⚡", "desc": "Authored 80+ production-grade measures.", "unlocked": True},
                        {"title": "Waterfall Wizard", "icon": "🌊", "desc": "Zero misallocation across tranches.", "unlocked": True},
                        {"title": "ECL Engineer", "icon": "🎯", "desc": "IFRS 9 matches Excel crosscheck within 0.00% variance.", "unlocked": True},
                        {"title": "Performance Hawk", "icon": "🦅", "desc": "All queries execute in <100ms.", "unlocked": True},
                        {"title": "Early Warning Champion", "icon": "🛡️", "desc": "Detected 2022 vintage roll acceleration prior to trigger breach.", "unlocked": True},
                        {"title": "Crisis Survivor", "icon": "🔥", "desc": "Successfully mitigated Level 8 market shock.", "unlocked": True}
                    ]
                }
            else:
                data = {"status": "ok", "message": "Securitisation AI Agent API v1.0"}

            self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
        else:
            # Default static file serving (index.html, css, js)
            if path == '/' or path == '':
                self.path = '/index.html'
            super().do_GET()

def run_server(port=8501):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SecuritisationAPIHandler)
    print(f" Securitisation Risk Arena & Analytics Server running at http://localhost:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n Server stopped.")
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8501
    run_server(port)

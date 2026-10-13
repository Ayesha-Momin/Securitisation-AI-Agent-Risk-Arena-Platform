"""
Securitisation AI Agent - Interactive Platform Launcher
=======================================================
Launches the local analytics dashboard server at http://localhost:8501
Usage:
    python run_app.py [port]
"""

import sys
import webbrowser
from app.server import run_server

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8501
    print("=" * 70)
    print("  SECURITISATION AI AGENT - RISK ARENA & ANALYTICS DASHBOARD")
    print(f"  Access URL: http://localhost:{port}/")
    print("=" * 70)
    try:
        webbrowser.open(f"http://localhost:{port}/")
    except Exception:
        pass
    run_server(port)

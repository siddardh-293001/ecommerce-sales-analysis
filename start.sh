#!/usr/bin/env bash
set -euo pipefail
exec python -m streamlit run app.py --server.address 0.0.0.0 --server.port "${PORT:-8501}" --server.headless true --browser.gatherUsageStats false

#!/usr/bin/env bash
set -euo pipefail
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ARROW_NUM_THREADS=1
exec python -m streamlit run app.py --server.address 0.0.0.0 --server.port "${PORT:-8501}" --server.headless true --browser.gatherUsageStats false

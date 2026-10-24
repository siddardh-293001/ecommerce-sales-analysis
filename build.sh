#!/usr/bin/env bash
set -euo pipefail
python -m pip install -r requirements.txt
python download_data.py
python prepare_dashboard.py

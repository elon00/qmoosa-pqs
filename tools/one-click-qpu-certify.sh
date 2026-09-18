#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "QMoosa-PQS ONE-CLICK QPU CERTIFICATION"
python3 tools/one-click-qpu-certify.py

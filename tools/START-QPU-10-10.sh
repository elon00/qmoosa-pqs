#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd)"
cd "$DIR"
if [ -f "tools/one-click-qpu-certify.py" ]; then
  RUNNER="tools/one-click-qpu-certify.py"
else
  RUNNER="one-click-qpu-certify.py"
fi
echo "========================================================="
echo "  BOUNTYHUNTER OS: CANONICAL QPU 10/10 CERTIFICATION"
echo "  Target: Physical Superconducting QPU (Dilution Fridge)"
echo "========================================================="
python3 "$RUNNER" "$@"
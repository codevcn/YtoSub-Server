#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$0")"

echo "=== [deploy] Starting full deploy sequence ==="

echo ""
echo ">>> Step 1/4: Pull latest code"
bash "$SCRIPT_DIR/i-pull.sh"

echo ""
echo ">>> Step 2/4: Build environment & Install dependencies"
bash "$SCRIPT_DIR/i-build.sh"

echo ""
echo ">>> Step 3/4: Run pre-flight tests"
bash "$SCRIPT_DIR/i-test.sh"

echo ""
echo ">>> Step 4/4: Restart systemd service"
bash "$SCRIPT_DIR/run-app.sh"
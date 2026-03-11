#!/bin/bash
set -e

echo "=== [deploy] Starting full deploy sequence ==="

# Xử lý vấn đề file có định dạng Windows (CRLF) gây lỗi khi chạy trên Linux.
cd /var/www/ytosub/shared
sed -i 's/\r$//' *.env
cd /var/www/ytosub/current
sed -i 's/\r$//' *.sh

SCRIPT_DIR="$(dirname "$0")"

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
#!/bin/bash

# Health Check Test Script for YtoSub Server
# Kiểm tra trạng thái hoạt động của API server

echo "=========================================="
echo "YtoSub Server - Health Check Test"
echo "=========================================="
echo ""

# Load configuration from deploy-data.env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "${SCRIPT_DIR}/deploy-data.env" ]; then
    source "${SCRIPT_DIR}/deploy-data.env"
    echo "✓ Loaded configuration from deploy-data.env"
else
    echo "⚠ Warning: deploy-data.env not found, using default port"
    PORT="8000"
fi

# Cấu hình
BASE_URL="http://localhost:${PORT}"
HEALTH_ENDPOINT="/api/v1/health"

echo "Testing endpoint: ${BASE_URL}${HEALTH_ENDPOINT}"
echo ""

# Thực hiện request và hiển thị kết quả
curl -X GET "${BASE_URL}${HEALTH_ENDPOINT}" \
  -H "Content-Type: application/json" \
  -w "\n\nHTTP Status Code: %{http_code}\n" \
  -s

echo ""
echo "=========================================="
echo "✅ Test completed!"
echo "=========================================="

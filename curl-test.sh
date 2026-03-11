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

HEALTH_ENDPOINT="/api/v1/health"
SOCKET_FILE="/var/www/ytosub/ytosub.sock"

echo ""

# Kiểm tra xem có file socket không để quyết định cách gọi curl
if [ -S "$SOCKET_FILE" ]; then
    echo "Testing endpoint via Unix Socket: $SOCKET_FILE"
    echo "URL: http://localhost${HEALTH_ENDPOINT}"
    echo ""
    
    # Thực hiện request qua Unix Socket
    curl -X GET "http://localhost${HEALTH_ENDPOINT}" \
      --unix-socket "$SOCKET_FILE" \
      -H "Content-Type: application/json" \
      -w "\n\nHTTP Status Code: %{http_code}\n" \
      -s
else
    BASE_URL="http://localhost:${PORT}"
    echo "Testing endpoint via Port: ${BASE_URL}${HEALTH_ENDPOINT}"
    echo ""

    # Thực hiện request qua Port mạng thông thường
    curl -X GET "${BASE_URL}${HEALTH_ENDPOINT}" \
      -H "Content-Type: application/json" \
      -w "\n\nHTTP Status Code: %{http_code}\n" \
      -s
fi

echo ""
echo "=========================================="
echo "✅ Test completed!"
echo "=========================================="
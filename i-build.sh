#!/bin/bash
set -e

source "$(dirname "$0")/deploy-data.env"

echo "=== [i-build] Preparing Virtual Environment & Dependencies ==="

# Đảm bảo dùng chung venv từ thư mục shared để không phải cài lại từ đầu
VENV_DIR="/var/www/ytosub/shared/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo ">> No shared venv found at '$VENV_DIR'. Creating..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# Nâng cấp pip và cài đặt thư viện
echo ">> Upgrading pip..."
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    echo ">> Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
fi

echo "=== ✅ [i-build] Environment ready. ==="
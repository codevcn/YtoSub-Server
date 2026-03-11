#!/bin/bash
set -e

source "$(dirname "$0")/deploy-data.env"

echo "=== [i-build] Starting YtoSub Server ==="

# Tạo venv nếu chưa có
if [ ! -d "$VENV_DIR" ]; then
    echo ">> No venv found at '$VENV_DIR'. Creating..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# Cài dependencies nếu có requirements.txt
if [ -f "requirements.txt" ]; then
    echo ">> Installing dependencies..."
    pip install -r requirements.txt
fi

echo ">> Starting uvicorn server..."
uvicorn src.main:app --reload --host $HOST --port $PORT

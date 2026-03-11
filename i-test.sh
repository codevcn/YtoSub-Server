#!/bin/bash
set -e

source "$(dirname "$0")/deploy-data.env"

echo "=== [i-test] Running pre-flight tests ==="

if [ ! -d "$VENV_DIR" ]; then
    echo "ERROR: Virtual environment '$VENV_DIR' not found."
    exit 1
fi

source "$VENV_DIR/bin/activate"

echo ""
echo "[1/2] Checking imports..."
# Khai báo PYTHONPATH để đảm bảo việc import từ src hoạt động đúng
PYTHONPATH="/var/www/ytosub/current" python -c "
from src.main import app
print('  app import: OK')
"

echo ""
echo "[2/2] Checking environment variables..."
python -c "
from src.configs.app_configs import get_settings
s = get_settings()
print(f'  GEMINI_MODEL          : {s.gemini_model}')
print(f'  TRANSLATE_CHUNK_SIZE  : {s.translate_chunk_size}')
print('  Env vars: OK')
"

echo "=== ✅ [i-test] All checks passed. ==="
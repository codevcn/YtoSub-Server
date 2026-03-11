#!/bin/bash
set -e

source "$(dirname "$0")/deploy-data.env"

echo "=== [i-test] Running pre-flight tests ==="

# Kiểm tra venv tồn tại
if [ ! -d "$VENV_DIR" ]; then
    echo "ERROR: Virtual environment '$VENV_DIR' not found. Run i-build.sh first."
    exit 1
fi

source "$VENV_DIR/bin/activate"

echo ""
echo "[1/2] Checking imports..."
python -c "
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
print(f'  results_base_dir      : {s.results_base_dir}')
print(f'  subtitles_base_dir    : {s.subtitles_base_dir}')
print(f'  database_url          : {s.database_url}')
print('  Env vars: OK')
"

echo ""
echo "=== [i-test] All checks passed. Safe to run i-build.sh ==="

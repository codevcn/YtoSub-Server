#!/bin/bash
set -e

# Load cấu hình
source "$(dirname "$0")/deploy-data.env"

echo "=== [i-pull] Pulling latest code and linking env files ==="

# 1. Reset code về bản mới nhất từ GitHub
echo ">> Resetting local changes..."
git fetch origin
git reset --hard origin/$GIT_BRANCH

# 2. Thiết lập đường dẫn
SHARED_DIR="/var/www/ytosub/shared"

# 3. Liên kết các tệp cấu hình (Environment files)
echo ">> Symlinking environment files..."
ln -sf "$SHARED_DIR/.env" .env
ln -sf "$SHARED_DIR/.gemini_key.env" .gemini_key.env
ln -sf "$SHARED_DIR/deploy-data.env" deploy-data.env

echo "=== ✅ [i-pull] Done. Pulling successfully. ==="
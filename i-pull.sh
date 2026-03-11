#!/bin/bash
set -e

echo "=== [i-pull] Pulling latest code and linking env files ==="

SHARED_DIR="/var/www/ytosub/shared"

# 1. Liên kết các tệp cấu hình (Environment files) trước khi source
echo ">> Symlinking environment files..."
ln -sf "$SHARED_DIR/.env" .env
ln -sf "$SHARED_DIR/.gemini_key.env" .gemini_key.env
ln -sf "$SHARED_DIR/deploy-data.env" deploy-data.env

# 2. Tải cấu hình
source "$(dirname "$0")/deploy-data.env"

# 3. Reset mã nguồn về bản mới nhất từ nhánh trên GitHub
echo ">> Resetting local changes..."
git fetch origin
git reset --hard origin/$GIT_BRANCH

echo "=== ✅ [i-pull] Done. Pulling successfully. ==="
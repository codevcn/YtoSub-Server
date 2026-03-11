#!/bin/bash
set -e

source "$(dirname "$0")/deploy-data.env"

echo "=== [i-pull] Pulling latest code from GitHub ==="

# Reset code về bản mới nhất
echo ">> Resetting local changes..."
git fetch origin
git reset --hard origin/$GIT_BRANCH

# Tạo liên kết mềm cho tất cả các file .env từ thư mục shared
echo ">> Symlinking environment files from shared/..."
SHARED_DIR="/var/www/ytosub/shared"
ln -sf "$SHARED_DIR/.env" .env
ln -sf "$SHARED_DIR/.gemini_key.env" .gemini_key.env
ln -sf "$SHARED_DIR/deploy-data.env" deploy-data.env

echo "=== ✅ [i-pull] Done. Working tree is clean and up-to-date. ==="
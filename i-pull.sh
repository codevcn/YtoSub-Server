#!/bin/bash
set -e

source "$(dirname "$0")/deploy-data.env"

echo "=== [i-pull] Pulling latest code from GitHub ==="

# Reset toàn bộ thay đổi tracked files về trạng thái remote (không xóa file untracked như .env)
echo ">> Resetting local changes..."
git fetch origin
git reset --hard origin/$GIT_BRANCH

echo "=== [i-pull] Done. Working tree is clean and up-to-date. ==="

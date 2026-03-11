#!/bin/bash
set -e

echo "=== [run-app] Restarting YtoSub Server (Systemd) ==="

# Khởi động lại service bằng quyền sudo. 
# Lưu ý: User 'deploy' cần được cấp quyền chạy lệnh systemctl restart ytosub mà không cần pass sudo.
sudo systemctl restart ytosub

# Kiểm tra trạng thái service xem có lên xanh (active) không
sudo systemctl status ytosub --no-pager | grep "Active:"

echo "=== ✅ [run-app] Server successfully restarted. ==="
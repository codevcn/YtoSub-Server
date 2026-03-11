# 🚀 Quy trình Deploy YtoSub Server (FastAPI) trên Ubuntu VPS

Tài liệu này hướng dẫn chi tiết cách triển khai server FastAPI lên VPS 2 vCPU, hỗ trợ SSE (Streaming) và xử lý các tác vụ dài (timeout 20 phút).

## 🛠️ THÔNG SỐ CẤU HÌNH

- **Domain:** `ytosub.vnote.io.vn`
- **IP:** `34.124.219.246`
- **Thư mục ứng dụng:** `/var/www/ytosub`
- **User thực thi:** `deploy`
- **Worker Gunicorn:** 5 (Công thức: $(2 \times 2) + 1 = 5$)

**Cấu trúc thư mục (current/releases model):**

```
/var/www/ytosub/
├── current -> releases/20260311120000/   # symlink trỏ tới release đang chạy
├── releases/
│   ├── 20260311120000/                  # mỗi lần deploy tạo 1 thư mục mới
│   └── ...
├── shared/
│   ├── .env                            # biến môi trường dùng chung
│   ├── venv/                           # môi trường ảo Python dùng chung
│   └── data/                           # dữ liệu bền vững (uploads, DB...)
└── ytosub.sock                         # Unix socket của Gunicorn
```

---

## PHẦN 1: CHUẨN BỊ USER & THƯ MỤC

Thực hiện dưới quyền `root` hoặc user có quyền `sudo`:

```bash
# 1. Tạo user deploy (nếu chưa có)
sudo adduser deploy

# 2. Tạo cấu trúc thư mục current/releases
sudo mkdir -p /var/www/ytosub/{releases,shared/data,shared/venv,shared/db}
sudo chown -R deploy:www-data /var/www/ytosub
sudo chmod -R 775 /var/www/ytosub

# 3. Tạo thư mục log
sudo mkdir -p /var/log/ytosub
sudo chown -R deploy:www-data /var/log/ytosub

```

---

## PHẦN 2: CÀI ĐẶT MÔI TRƯỜNG & CODE

Chuyển sang user `deploy` để thực hiện:

```bash
sudo su - deploy
cd /var/www/ytosub

# 1. Thiết lập venv dùng chung trong shared/
python3 -m venv shared/venv
source shared/venv/bin/activate
pip install --upgrade pip
pip install gunicorn uvicorn

# 2. Tạo file .env dùng chung và dán API Key vào
nano shared/.env

# 3. Clone code vào release đầu tiên
RELEASE=$(date +%Y%m%d%H%M%S)
git clone https://github.com/codevcn/YtoSub-Server.git releases/$RELEASE

# 4. Cài đặt dependencies vào shared/venv
pip install -r releases/$RELEASE/requirements.txt

# 5. Liên kết .env từ shared vào release
ln -s /var/www/ytosub/shared/.env releases/$RELEASE/.env

# 6. Trỏ symlink current vào release đầu tiên
ln -sfn /var/www/ytosub/releases/$RELEASE /var/www/ytosub/current

```

---

## PHẦN 3: CẤU HÌNH GUNICORN (SYSTEMD)

Quay lại user sudo để tạo file service: `sudo nano /etc/systemd/system/ytosub.service`

**Nội dung file:**

```ini
[Unit]
Description=Gunicorn instance to serve YtoSub Server
After=network.target

[Service]
User=deploy
Group=www-data
WorkingDirectory=/var/www/ytosub/current
Environment="PATH=/var/www/ytosub/shared/venv/bin"
# Timeout 1200s (20 phút) để xử lý các tác vụ AI dài
ExecStart=/var/www/ytosub/shared/venv/bin/gunicorn \
    -w 5 \
    -k uvicorn.workers.UvicornWorker \
    --timeout 1200 \
    --keep-alive 5 \
    --access-logfile /var/log/ytosub/access.log \
    --error-logfile /var/log/ytosub/error.log \
    main:app \
    --bind unix:/var/www/ytosub/ytosub.sock

[Install]
WantedBy=multi-user.target

```

---

## PHẦN 4: CẤU HÌNH NGINX (REVERSE PROXY & SSE)

Tạo file: `sudo nano /etc/nginx/sites-available/ytosub.vnote.io.vn`

**Nội dung file:**

```nginx
# Upstream trỏ tới Unix socket của Gunicorn (5 workers)
upstream ytosub_backend {
    server unix:/var/www/ytosub/ytosub.sock fail_timeout=0;
}

server {
    listen 80;
    server_name ytosub.vnote.io.vn;

    # Hỗ trợ file upload lớn (subtitle, v.v.)
    client_max_body_size 100M;

    # --- SSE endpoint: /api/v1/video/sse ---
    # Cần tắt buffering hoàn toàn để stream sự kiện real-time tới client
    location /api/v1/video/sse {
        include proxy_params;
        proxy_pass http://ytosub_backend;

        proxy_http_version 1.1;
        proxy_set_header Connection "";

        # Timeout 20 phút — tác vụ dịch AI có thể chạy lâu
        proxy_read_timeout 1200s;
        proxy_send_timeout 1200s;

        # Tắt toàn bộ buffering để SSE event được gửi ngay lập tức
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding on;
        add_header 'X-Accel-Buffering' 'no';
        add_header 'Cache-Control' 'no-cache';
    }

    # --- Tất cả các route còn lại (/api/v1/video/translate, /file, /subtitle, ...) ---
    location / {
        include proxy_params;
        proxy_pass http://ytosub_backend;

        proxy_http_version 1.1;
        proxy_set_header Connection "";

        # Timeout 20 phút cho tác vụ dịch chạy nền (POST /video/translate)
        proxy_connect_timeout 1200s;
        proxy_send_timeout 1200s;
        proxy_read_timeout 1200s;
    }
}

```

**Kích hoạt cấu hình:**

```bash
sudo ln -s /etc/nginx/sites-available/ytosub.vnote.io.vn /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

```

---

## PHẦN 5: SSL & KHỞI CHẠY HỆ THỐNG

```bash
# Cấp chứng chỉ SSL miễn phí
sudo certbot --nginx -d ytosub.vnote.io.vn

# Khởi chạy dịch vụ FastAPI
sudo systemctl daemon-reload
sudo systemctl start ytosub
sudo systemctl enable ytosub

```

---

## PHẦN 6: DUY TRÌ & CẬP NHẬT (DEPLOY.SH)

Tạo file `deploy.sh` tại `/var/www/ytosub/deploy.sh` (Sở hữu bởi user `deploy`):

```bash
#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$0")"

echo "=== [deploy] Starting full deploy sequence ==="

echo ""
echo ">>> Step 1/4: Pull latest code"
bash "$SCRIPT_DIR/i-pull.sh"

echo ""
echo ">>> Step 2/4: Build environment & Install dependencies"
bash "$SCRIPT_DIR/i-build.sh"

echo ""
echo ">>> Step 3/4: Run pre-flight tests"
bash "$SCRIPT_DIR/i-test.sh"

echo ""
echo ">>> Step 4/4: Restart systemd service"
bash "$SCRIPT_DIR/run-app.sh"
```

---

### 🔍 LỆNH KIỂM TRA NHANH

- **Xem log thực tế (SSE):** `./log.sh`
- **Kiểm tra lỗi Python:** `journalctl -u ytosub -f`
- **Kiểm tra socket:** `ls -l /var/www/ytosub/ytosub.sock`

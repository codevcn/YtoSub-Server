Dưới đây là bản **Checklist chuẩn A-Z** đã được tối ưu hóa riêng cho cấu hình VPS 2 vCPU của bạn, tích hợp luồng xử lý SSE và mức timeout 20 phút cho dự án "YtoSub Server".

---

## 🏗️ PHẦN 1: CẤU HÌNH TÊN MIỀN (DNS)

1. Truy cập quản trị tại **Tenten**.
2. Thêm bản ghi **A Record**:

- **Host:** `ytosub`
- **Value:** `34.124.219.246`

3. Kiểm tra bằng lệnh `ping ytosub.vnote.io.vn` trên máy cá nhân để chắc chắn IP đã thông.

---

## 📂 PHẦN 2: CHUẨN BỊ MÔI TRƯỜNG & CODE

1. **Cập nhật hệ thống:**

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git -y

```

2. **Tổ chức thư mục (Khuyên dùng /var/www để tránh lỗi quyền hạn Nginx):**

```bash
sudo mkdir -p /var/www/YtoSub-Server
sudo chown $USER:$USER /var/www/YtoSub-Server
cd /var/www/YtoSub-Server

```

3. **Clone và cài đặt:**

```bash
git clone https://github.com/codevcn/YtoSub-Server.git .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn uvicorn

```

4. **Thiết lập biến môi trường:** Tạo file `.env` và dán API Key của Google GenAI vào.

---

## ⚙️ PHẦN 3: CẤU HÌNH GUNICORN (QUẢN LÝ TIẾN TRÌNH)

Vì bạn có 2 vCPU và tác vụ là I/O bound (đợi API), chúng ta sẽ dùng công thức:
$Workers = (2 \times 2) + 1 = 5$

1. **Tạo file log:**

```bash
sudo mkdir -p /var/log/ytosub
sudo chown $USER:$USER /var/log/ytosub

```

2. **Tạo Systemd Service:** `sudo nano /etc/systemd/system/ytosub.service`
3. **Dán nội dung (Đã chỉnh timeout 1200s):**

```ini
[Unit]
Description=Gunicorn instance to serve YtoSub Server
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/YtoSub-Server
Environment="PATH=/var/www/YtoSub-Server/venv/bin"
ExecStart=/var/www/YtoSub-Server/venv/bin/gunicorn \
    -w 5 \
    -k uvicorn.workers.UvicornWorker \
    --timeout 1200 \
    --keep-alive 5 \
    --access-logfile /var/log/ytosub/access.log \
    --error-logfile /var/log/ytosub/error.log \
    main:app \
    --bind unix:ytosub.sock

[Install]
WantedBy=multi-user.target

```

---

## 🌐 PHẦN 4: CẤU HÌNH NGINX (REVERSE PROXY & SSE)

1. **Tạo file cấu hình:** `sudo nano /etc/nginx/sites-available/ytosub.vnote.io.vn`
2. **Dán nội dung (Tắt buffering để SSE chạy mượt):**

```nginx
server {
    listen 80;
    server_name ytosub.vnote.io.vn;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/YtoSub-Server/ytosub.sock;

        # Cấu hình Timeout 20 phút
        proxy_connect_timeout 1200s;
        proxy_send_timeout 1200s;
        proxy_read_timeout 1200s;

        # Cấu hình tối ưu cho SSE (Streaming)
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding on;
        add_header 'X-Accel-Buffering' 'no';
        add_header 'Cache-Control' 'no-cache';
    }
}

```

3. **Kích hoạt:**

```bash
sudo ln -s /etc/nginx/sites-available/ytosub.vnote.io.vn /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

```

---

## 🔒 PHẦN 5: SSL & KHỞI CHẠY

1. **Cấp SSL:**

```bash
sudo certbot --nginx -d ytosub.vnote.io.vn

```

2. **Chạy Service FastAPI:**

```bash
sudo systemctl daemon-reload
sudo systemctl start ytosub
sudo systemctl enable ytosub

```

---

## 🛠️ PHẦN 6: KIỂM TRA & DUY TRÌ

- **Xem tiến độ stream (Log):** `tail -f /var/log/ytosub/access.log`
- **Kiểm tra lỗi nếu có:** `journalctl -u ytosub -f`
- **Cập nhật code nhanh:** Tạo một file `deploy.sh` với nội dung:

```bash
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ytosub
echo "YtoSub Server updated!"

```

## Lệnh git ko làm mất quyền của file trên server

```bash
git update-index --add --chmod=+x deploy.sh
git update-index --add --chmod=+x i-pull.sh
git update-index --add --chmod=+x i-build.sh
git update-index --add --chmod=+x i-test.sh
git update-index --add --chmod=+x log.sh
git update-index --add --chmod=+x run-app.sh
git update-index --add --chmod=+x curl-test.sh

git update-index --add --chmod=+x deploy.sh && git update-index --add --chmod=+x i-pull.sh && git update-index --add --chmod=+x i-build.sh && git update-index --add --chmod=+x i-test.sh && git update-index --add --chmod=+x log.sh && git update-index --add --chmod=+x run-app.sh && git update-index --add --chmod=+x curl-test.sh
```

## Chạy lệnh để đổi từ CRLF sang LF

Cần chạy lệnh này trên máy local trước khi push code lên server để tránh lỗi "$'\r': command not found" do Windows sử dụng CRLF làm ký tự xuống dòng, trong khi Linux dùng LF. Lệnh này sẽ chuyển đổi tất cả các file trong repo sang định dạng LF, giúp script chạy bình thường trên server Linux.

```bash
git config --global core.autocrlf false
```

## Xem log của server trên Ubuntu VPS

1. Xem log thực tế trong runtime (Application Logs)

Đây là lệnh để theo dõi trực tiếp các hoạt động diễn ra bên trong mã nguồn Python của bạn.

- Mục đích: Xem các dòng print(), thông báo lỗi (Traceback) khi code bị crash, hoặc các thông tin debug mà bạn ghi vào file log.
- Khi nào cần dùng: Khi bạn muốn kiểm tra xem logic ứng dụng có chạy đúng không (ví dụ: "Environment variables loaded...", "Database connected...").
- Tham số -f: Viết tắt của "Follow", giúp màn hình tự động cập nhật dòng mới nhất ngay khi nó xuất hiện.

```bash
tail -f /var/log/ytosub/error.log
```

2. Xem log realtime của server (System/Process Logs)

Lệnh này truy cập vào nhật ký của trình quản lý hệ thống (Systemd). Nó tập trung vào trạng thái sống còn của toàn bộ tiến trình Gunicorn.

- Mục đích: Theo dõi quá trình khởi động, restart của service, và các lỗi hệ thống cấp cao (như sai đường dẫn venv, lỗi quyền truy cập file socket, hoặc lỗi khiến worker bị "Halt").
- Khi nào cần dùng: Khi bạn vừa chạy systemctl restart và muốn biết service có lên "Active (running)" thành công hay không.
- Tham số -u: Chỉ định "Unit" (tên service) cần xem log để tránh bị lẫn với log của các dịch vụ khác trong VPS.

```bash
journalctl -u ytosub.service -f
```

3. Xem log snapshot (Snapshot Logs)

Nếu bạn chỉ muốn xem một "snapshot" tức thời của log mà không cần theo dõi liên tục, có thể dùng lệnh này:

```bash
journalctl -u ytosub.service -n 100 --no-pager
```

## Lệnh chuyển đổi định dạng xuống dòng từ Windows (CRLF) sang Linux (LF)

```bash
cd /var/www/ytosub/shared
sed -i 's/\r$//' *.env
cd /var/www/ytosub/current
sed -i 's/\r$//' *.sh
```

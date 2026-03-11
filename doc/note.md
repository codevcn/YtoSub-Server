## lệnh git ko làm mất quyền của file trên server

```bash
git update-index --add --chmod=+x deploy.sh
git update-index --add --chmod=+x i-pull.sh
git update-index --add --chmod=+x i-build.sh
git update-index --add --chmod=+x i-test.sh
git update-index --add --chmod=+x log.sh
git update-index --add --chmod=+x run-app.sh

git update-index --add --chmod=+x deploy.sh && git update-index --add --chmod=+x i-pull.sh && git update-index --add --chmod=+x i-build.sh && git update-index --add --chmod=+x i-test.sh && git update-index --add --chmod=+x log.sh && git update-index --add --chmod=+x run-app.sh
```

## chạy lệnh để đổi từ CRLF sang LF

Cần chạy lệnh này trên máy local trước khi push code lên server để tránh lỗi "$'\r': command not found" do Windows sử dụng CRLF làm ký tự xuống dòng, trong khi Linux dùng LF. Lệnh này sẽ chuyển đổi tất cả các file trong repo sang định dạng LF, giúp script chạy bình thường trên server Linux.

```bash
git config --global core.autocrlf false
```

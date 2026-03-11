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

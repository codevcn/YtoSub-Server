# Tài liệu Triển khai Server-Sent Events (SSE) với FastAPI

Tài liệu này hướng dẫn cách xây dựng một Server cung cấp luồng dữ liệu thời gian thực sử dụng framework **FastAPI** và thư viện **sse-starlette**.

---

## 1. Yêu cầu hệ thống

Để triển khai SSE một cách chuẩn chỉnh và dễ dàng nhất trên FastAPI, chúng ta sử dụng thư viện `sse-starlette`. Thư viện này giúp tự động hóa việc định dạng dữ liệu (data, event, id) và quản lý các Header HTTP.

**Cài đặt:**

```bash
pip install fastapi uvicorn sse-starlette

```

---

## 2. Quy trình triển khai trên Server

Luồng xử lý của FastAPI cho một kết nối SSE như sau:

1. **Tiếp nhận Request:** Client gửi một request GET đến endpoint.
2. **Khởi tạo Generator:** Server tạo ra một hàm `async generator` (sử dụng `yield`).
3. **Trả về EventSourceResponse:** FastAPI trả về một phản hồi đặc biệt giúp giữ kết nối mở.
4. **Đẩy dữ liệu:** Mỗi khi hàm generator `yield` ra một giá trị, nó sẽ được gửi ngay lập tức tới Client.
5. **Kết thúc:** Khi Client ngắt kết nối hoặc Generator kết thúc vòng lặp.

---

## 3. Code ví dụ chi tiết

Dưới đây là mã nguồn chuẩn cho một endpoint SSE xử lý tin nhắn theo thời gian thực.

```python
import asyncio
from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from datetime import datetime

app = FastAPI()

@app.get("/stream-events")
async def event_stream(request: Request):
    """
    Endpoint cung cấp luồng dữ liệu thời gian thực.
    """
    async def event_generator():
        while True:
            # 1. Kiểm tra nếu Client đã ngắt kết nối thì dừng generator
            if await request.is_disconnected():
                print("Client disconnected")
                break

            # 2. Giả lập lấy dữ liệu từ Database hoặc Message Queue
            current_time = datetime.now().strftime("%H:%M:%S")
            data = {
                "message": "Cập nhật dữ liệu hệ thống",
                "time": current_time
            }

            # 3. Yield dữ liệu theo định dạng của sse-starlette
            # Nó sẽ tự động format thành: data: {...}\n\n
            yield {
                "event": "update",  # Tên sự kiện (tùy chọn)
                "id": f"msg_{current_time}", # ID để client có thể resume (tùy chọn)
                "retry": 5000,      # Thời gian client thử kết nối lại nếu lỗi (ms)
                "data": data        # Dữ liệu chính (dict sẽ tự động được JSON stringify)
            }

            # 4. Chờ một khoảng thời gian trước khi gửi event tiếp theo
            await asyncio.sleep(3)

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

```

---

## 4. Các thông số cấu hình quan trọng

Khi làm việc với SSE trong môi trường Python/FastAPI, bạn cần lưu ý:

| Thành phần                      | Ý nghĩa                                                                                  |
| ------------------------------- | ---------------------------------------------------------------------------------------- |
| **`async def`**                 | Bắt buộc sử dụng để không làm nghẽn (block) Worker của Server khi duy trì nhiều kết nối. |
| **`request.is_disconnected()`** | Cực kỳ quan trọng để giải phóng tài nguyên hệ thống khi người dùng tắt trình duyệt.      |
| **`yield`**                     | Dùng để đẩy từng tin nhắn đi mà không đóng kết nối HTTP.                                 |
| **`EventSourceResponse`**       | Tự động thiết lập Header `Content-Type: text/event-stream`.                              |

---

## 5. Lưu ý khi Deploy (Sản xuất)

### Tối ưu hóa Nginx (Reverse Proxy)

Nếu bạn chạy FastAPI sau Nginx, bạn **phải** tắt tính năng đệm (buffering), nếu không Nginx sẽ giữ lại dữ liệu cho đến khi đủ lớn mới gửi về trình duyệt, gây ra hiện tượng lag.

**Cấu hình Nginx:**

```nginx
location /stream-events {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    chunked_transfer_encoding off;
    proxy_buffering off; # Tắt buffer để dữ liệu đi ngay lập tức
    proxy_cache off;
}

```

### Quản lý số lượng kết nối

Mỗi kết nối SSE là một kết nối HTTP mở liên tục.

- Hãy đảm bảo Worker của bạn (Uvicorn/Gunicorn) được cấu hình sử dụng lớp **worker async** (như `uvloop`) để có thể xử lý hàng nghìn kết nối đồng thời.
- Nếu server có quá nhiều kết nối, hãy cân nhắc sử dụng **Redis Pub/Sub** để điều phối tin nhắn thay vì truy vấn database trong vòng lặp `while True`.

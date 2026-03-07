# FastAPI Development Best Practices & Coding Standards

Tài liệu này quy định các tiêu chuẩn viết code cho Server FastAPI, tập trung vào ba trụ cột: **Hiệu năng cao**, **Sự đơn giản** và **Tính tiện lợi** trong bảo trì.

## 1. Tối ưu hóa Hiệu năng (Performance)

- **Lập trình Bất đồng bộ (Async/Await):**
  - Sử dụng `async def` cho các tác vụ I/O bound (truy vấn DB, gọi API bên thứ ba).
  - Sử dụng `def` truyền thống cho các tác vụ tính toán nặng (CPU bound) để FastAPI xử lý trong thread pool riêng.
- **Pydantic V2:** Luôn sử dụng phiên bản Pydantic mới nhất để tận dụng tốc độ kiểm thử dữ liệu (validation) nhanh gấp nhiều lần nhờ nhân Rust.
- **Thư viện JSON thay thế:** Cài đặt và cấu hình `orjson` hoặc `ujson` trong `DefaultResponseClass` để tăng tốc độ đóng gói dữ liệu trả về.
- **Background Tasks:** Sử dụng `fastapi.BackgroundTasks` cho các công việc không cần trả kết quả ngay (gửi email, log sự kiện) để giảm độ trễ của request.

## 2. Sự đơn giản và Tiện lợi (Simplicity & Convenience)

- **Dependency Injection (Hệ thống phụ thuộc):**
  - Tận dụng `Depends` để quản lý kết nối cơ sở dữ liệu, xác thực (Authentication) và phân quyền (Authorization).
  - Giữ cho các hàm logic trong endpoint gọn gàng bằng cách đẩy việc chuẩn bị dữ liệu vào các Dependencies.
- **Pydantic Schemas:**
  - Luôn khai báo `response_model` để tự động hóa việc lọc dữ liệu và tạo tài liệu API.
  - Tách biệt Schema cho `Create`, `Update` và `Read` để kiểm soát dữ liệu đầu vào/đầu ra chặt chẽ.
- **Tài liệu tự động (OpenAPI):**
  - Viết mô tả chi tiết trong `docstrings` của hàm.
  - Sử dụng các tham số `summary`, `description`, và `tags` trong decorator để tối ưu hóa giao diện `/docs`.

## 3. Cấu trúc Dự án và Module hóa (Architecture)

- **Sử dụng APIRouter:**
  - Chia nhỏ ứng dụng thành các module chức năng (ví dụ: `auth`, `users`, `products`).
  - Mỗi module đặt trong một tệp riêng theo quy tắc **snake_case**.
- **Quản lý cấu hình (Settings):**
  - Sử dụng `pydantic-settings` để quản lý biến môi trường từ tệp `.env`.
  - Đảm bảo tất cả cấu hình hệ thống được định nghĩa kiểu dữ liệu (Type Hinting).
- **Middleware tối giản:** Chỉ sử dụng Middleware cho các yêu cầu toàn cục như CORS, GZip hoặc xử lý thời gian phản hồi (Process time).

## 4. Tiêu chuẩn Viết Code "Sạch" cho AI Agent

- **Type Hinting tuyệt đối:** Mọi tham số đầu vào và giá trị trả về của hàm phải được định nghĩa kiểu dữ liệu rõ ràng (ví dụ: `Union[str, None]`, `List[int]`).
- **Xử lý lỗi tập trung:**
  - Sử dụng `fastapi.HTTPException` để trả về lỗi đúng chuẩn RESTful.
  - Định nghĩa các `exception_handlers` tùy chỉnh nếu cần cấu trúc lỗi đặc thù.
- **Quản lý tài nguyên:** Sử dụng từ khóa `yield` trong các Dependency để đảm bảo tài nguyên (như Database session) luôn được đóng sau khi hoàn thành request.
- **Naming Convention:** Tuân thủ nghiêm ngặt **snake_case** cho tên tệp, tên biến và tên hàm.

## 5. Danh mục Thư viện Khuyến nghị (Tech Stack)

| Thành phần         | Thư viện đề xuất                                |
| :----------------- | :---------------------------------------------- |
| **ORM / Database** | SQLAlchemy (Async), Tortoise-ORM, hoặc SQLModel |
| **Migration**      | Alembic                                         |
| **Validation**     | Pydantic V2                                     |
| **Settings**       | Pydantic-settings                               |
| **Logging**        | Loguru                                          |
| **Client/Testing** | HTTPX                                           |

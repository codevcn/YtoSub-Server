# Quy tắc Phát triển và Cấu trúc Dự án (AI Agent Rules)

Để đảm bảo tính nhất quán, khả năng bảo trì và khả năng mở rộng của hệ thống, AI Agent cần tuân thủ nghiêm ngặt các quy tắc dưới đây khi thực hiện các nhiệm vụ lập trình:

## 1. Quy định về Đặt tên Tệp (Naming Convention)

- Tất cả các tệp tin trong dự án phải được đặt tên theo định dạng **snake_case** (ví dụ: `api_handler.py`, `database_connection.js`, `user_service.ts`).
- Không sử dụng khoảng trắng, ký tự đặc biệt hoặc CamelCase trong tên tệp.

## 2. Cấu trúc Mã nguồn và Tính Mô-đun (Code Separation)

- **Tách biệt mã nguồn:** Không viết tất cả logic vào một tệp duy nhất. Phải chia nhỏ mã nguồn thành các mô-đun hoặc component riêng biệt dựa trên chức năng (ví dụ: tách biệt logic xử lý dữ liệu, định nghĩa giao diện và các hàm bổ trợ).
- **Khả năng bảo trì:** Cấu trúc mã nguồn phải được thiết kế sao cho dễ dàng cập nhật và sửa lỗi mà không ảnh hưởng đến toàn bộ hệ thống.
- **Khả năng mở rộng:** Ưu tiên sử dụng các design patterns phù hợp để hệ thống có thể tích hợp thêm tính năng mới trong tương lai một cách dễ dàng.

## 3. Chuẩn hóa API (API Standards)

- Mọi route API được tạo ra hoặc cập nhật phải tuân thủ nghiêm ngặt tiêu chuẩn **OpenAPI (Swagger)**.
- Yêu cầu đối với mỗi API route:
  - Có định nghĩa rõ ràng về `Path Parameters`, `Query Parameters`, và `Request Body`.
  - Cung cấp đầy đủ các mã trạng thái phản hồi (Response Status Codes) như `200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`, `500 Internal Server Error`.
  - Mô tả chi tiết kiểu dữ liệu đầu ra (Schema) cho từng trường hợp thành công và thất bại.

## 4. Quy tắc Phát triển và Tiêu chuẩn Viết Code (Coding Standards)

- Mọi đoạn mã phải tuân thủ các tiêu chuẩn viết code đã được quy định từ tài liệu **FastAPI Development Best Practices & Coding Standards** trong file `agent-skills/fastapi_coding_standards.md`.

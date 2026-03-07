import asyncio


class SSEConnectionManager:
    def __init__(self) -> None:
        # Lưu trữ danh sách Queue của các client đang kết nối
        # Key: task_id (định dạng: "username:video_id")
        self._active_connections: dict[str, list[asyncio.Queue]] = {}

        # Lưu trạng thái cuối cùng để khi client reconnect sẽ nhận được ngay tiến độ mới nhất
        self._task_latest_event: dict[str, dict] = {}

    async def subscribe(self, task_id: str) -> asyncio.Queue:
        """Đăng ký một client mới vào tiến trình dịch."""
        queue = asyncio.Queue()
        if task_id not in self._active_connections:
            self._active_connections[task_id] = []
        self._active_connections[task_id].append(queue)

        # Reconnect Logic: Gửi ngay trạng thái cuối cùng (nếu có) để client cập nhật giao diện
        if task_id in self._task_latest_event:
            await queue.put(self._task_latest_event[task_id])

        return queue

    def unsubscribe(self, task_id: str, queue: asyncio.Queue) -> None:
        """Hủy đăng ký client khi họ ngắt kết nối."""
        if task_id in self._active_connections:
            if queue in self._active_connections[task_id]:
                self._active_connections[task_id].remove(queue)
            # Dọn dẹp key nếu không còn client nào lắng nghe
            if not self._active_connections[task_id]:
                del self._active_connections[task_id]

    def push_event(self, task_id: str, event_type: str, data: dict) -> None:
        """Đẩy sự kiện mới đến tất cả các client đang lắng nghe và quản lý bộ nhớ."""
        event = {"event": event_type, "data": data}

        # Phân phối event đến các hàng đợi (Queue) của client đang kết nối
        if task_id in self._active_connections:
            for queue in self._active_connections[task_id]:
                queue.put_nowait(event)

        # Logic quản lý trạng thái và dọn dẹp bộ nhớ
        if event_type in ("done", "error"):
            # Nếu tiến trình đã hoàn thành hoặc lỗi, xóa trạng thái cuối cùng để giải phóng RAM
            if task_id in self._task_latest_event:
                del self._task_latest_event[task_id]

            # Đồng thời đảm bảo không còn danh sách kết nối trống kẹt lại
            if task_id in self._active_connections:
                del self._active_connections[task_id]
        else:
            # Chỉ lưu lại trạng thái mới nhất cho các tiến trình đang thực sự chạy
            self._task_latest_event[task_id] = event


# Khởi tạo một instance toàn cục (Singleton) để dùng chung cho toàn bộ app
sse_manager = SSEConnectionManager()

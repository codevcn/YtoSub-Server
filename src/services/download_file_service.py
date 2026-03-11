import re
from pathlib import Path
from fastapi import HTTPException, status
from src.configs.app_configs import AppSettings

# Cho phép: chữ cái, số, dấu gạch dưới, gạch ngang, dấu chấm (dùng cho tên file)
_SAFE_SEGMENT = re.compile(r"^[a-zA-Z0-9_\-\.]+$")


class DownloadFileService:
    def __init__(self, settings: AppSettings) -> None:
        self._base_dir = settings.results_base_dir.resolve()

    def resolve_file_path(self, username: str, video_id: str, filename: str) -> Path:
        """Kiểm tra tính hợp lệ của các tham số, ngăn path traversal và trả về đường dẫn tuyệt đối của file."""
        for segment in (username, video_id, filename):
            if not _SAFE_SEGMENT.match(segment):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tham số không hợp lệ: '{segment}'",
                )

        file_path = (self._base_dir / username / video_id / filename).resolve()

        # Ngăn path traversal: sử dụng is_relative_to thay vì startswith để đảm bảo an toàn tuyệt đối
        if not file_path.is_relative_to(self._base_dir):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Truy cập bị từ chối.",
            )

        # Đảm bảo đối tượng cuối cùng thực sự là một tệp tin, không phải là một thư mục
        if not file_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File '{filename}' không tồn tại.",
            )

        return file_path

    def list_srt_files(self, username: str) -> list[dict]:
        """Quét thư mục của người dùng và trả về danh sách {video_id, filename} cho tất cả file .srt."""
        if not _SAFE_SEGMENT.match(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username không hợp lệ: '{username}'",
            )

        user_dir = (self._base_dir / username).resolve()

        # Tương tự, sử dụng is_relative_to để kiểm tra tính hợp lệ của đường dẫn
        if not user_dir.is_relative_to(self._base_dir):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Truy cập bị từ chối.",
            )

        # Trả về danh sách rỗng nếu thư mục người dùng chưa được tạo
        if not user_dir.is_dir():
            return []

        results: list[dict] = []
        for video_dir in sorted(user_dir.iterdir()):
            if video_dir.is_dir():
                for srt_file in sorted(video_dir.glob("*.srt")):
                    results.append(
                        {"video_id": video_dir.name, "filename": srt_file.name}
                    )

        return results

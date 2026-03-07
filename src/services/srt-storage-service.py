import os
from datetime import datetime

from src.configs.app_configs import AppSettings, root_dir


class SrtStorageService:
    def __init__(self, settings: AppSettings) -> None:
        self._base_dir = root_dir / settings.translate_results_dir

    def generate_path(self, video_id: str, username: str) -> str:
        """Tạo đường dẫn lưu file theo cấu trúc base_dir/youtube/{username}/YtoSub_{video_id}_{YYYY}-{MM}-{DD}-{HH}.srt"""
        now: datetime = datetime.now()
        timestamp = now.strftime("%Y-%m-%d-%H")
        dir_path = self._base_dir / "youtube" / username
        os.makedirs(dir_path, exist_ok=True)
        filename = f"YtoSub_{video_id}_{timestamp}.srt"
        return str(dir_path / filename)

    def save(self, content: str, video_id: str, username: str) -> str:
        """Ghi nội dung vào file tại đường dẫn được tạo bởi generate_path. Trả về đường dẫn file."""
        file_path: str = self.generate_path(video_id, username)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

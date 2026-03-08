import os
from datetime import datetime
from src.configs.app_configs import AppSettings


class TranslateStorageService:
    def __init__(self, settings: AppSettings) -> None:
        self._base_dir = settings.results_base_dir

    def generate_path(self, video_id: str, username: str) -> tuple[str, str]:
        """Tạo đường dẫn lưu file theo cấu trúc base_dir/youtube/{username}/{video_id}/YtoSub_{video_id}_{YYYY}-{MM}-{DD}-{HH}.srt"""
        now: datetime = datetime.now()
        timestamp = now.strftime("%Y-%m-%d-%H")
        dir_path = self._base_dir / username / video_id
        os.makedirs(dir_path, exist_ok=True)
        filename = f"YtoSub_{video_id}_{timestamp}.srt"
        return str(dir_path / filename), filename

    def save(self, content: str, video_id: str, username: str) -> str:
        """Ghi nội dung vào file tại đường dẫn được tạo bởi generate_path. Trả về đường dẫn file."""
        file_path: str = self.generate_path(video_id, username)[0]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path


class SummaryStorageService:
    def __init__(self, settings: AppSettings) -> None:
        self._base_dir = settings.results_base_dir

    def generate_path(self, video_id: str, username: str) -> tuple[str, str]:
        """Tạo đường dẫn lưu file tóm tắt theo cấu trúc base_dir/youtube/{username}/{video_id}/Summary_{video_id}_{YYYY}-{MM}-{DD}-{HH}.txt"""
        now: datetime = datetime.now()
        timestamp = now.strftime("%Y-%m-%d-%H")
        dir_path = self._base_dir / username / video_id
        os.makedirs(dir_path, exist_ok=True)
        filename = f"Summary_{video_id}_{timestamp}.txt"
        return str(dir_path / filename), filename

    def save(self, content: str, video_id: str, username: str) -> str:
        """Ghi nội dung tóm tắt vào file tại đường dẫn được tạo bởi generate_path. Trả về đường dẫn file."""
        file_path: str = self.generate_path(video_id, username)[0]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path


class TranscriptStorageService:
    def __init__(self, settings: AppSettings) -> None:
        self._base_dir = settings.results_base_dir

    def generate_path(self, video_id: str, username: str) -> tuple[str, str]:
        """Tạo đường dẫn lưu file transcript theo cấu trúc base_dir/youtube/{username}/{video_id}/Transcript_{video_id}_{YYYY}-{MM}-{DD}-{HH}.txt"""
        now: datetime = datetime.now()
        timestamp = now.strftime("%Y-%m-%d-%H")
        dir_path = self._base_dir / username / video_id
        os.makedirs(dir_path, exist_ok=True)
        filename = f"Transcript_{video_id}_{timestamp}.txt"
        return str(dir_path / filename), filename

    def save(self, content: str, video_id: str, username: str) -> str:
        """Ghi nội dung transcript vào file tại đường dẫn được tạo bởi generate_path. Trả về đường dẫn file."""
        file_path: str = self.generate_path(video_id, username)[0]
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

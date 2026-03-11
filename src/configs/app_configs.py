import os
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from .roots import root_dir


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(root_dir / ".env"), str(root_dir / ".gemini_key.env")],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str
    gemini_model: str
    translate_chunk_size: int

    # Pydantic tự động ánh xạ (map) các biến môi trường dạng IN HOA (DATA_DIR)
    # vào các thuộc tính viết thường tương ứng ở đây.
    data_dir: str = "data"
    db_dir: str = "db"
    translate_results_dir: str = "results"
    uploaded_subtitles_dir: str = "subtitles"

    @computed_field
    @property
    def results_base_dir(self) -> Path:
        """Thư mục gốc lưu file kết quả"""
        base = Path(self.data_dir)
        # Kiểm tra nếu chưa phải đường dẫn tuyệt đối thì mới nối với root_dir
        if not base.is_absolute():
            base = root_dir / base
        print("Absolute results base dir:", base)
        return base / "youtube" / self.translate_results_dir

    @computed_field
    @property
    def subtitles_base_dir(self) -> Path:
        """Thư mục gốc lưu file phụ đề"""
        base = Path(self.data_dir)
        if not base.is_absolute():
            base = root_dir / base
        print("Absolute dir:", base)
        return base / "youtube" / self.uploaded_subtitles_dir

    @computed_field
    @property
    def database_url(self) -> str:
        """SQLite URL"""
        base = Path(self.db_dir)
        if not base.is_absolute():
            base = root_dir / base
        print("Absolute database dir:", base)
        os.makedirs(base, exist_ok=True)
        return f"sqlite:///{base / 'subtitles_app.db'}"


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()

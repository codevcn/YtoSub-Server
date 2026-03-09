import os
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

root_dir = Path(__file__).resolve().parent.parent.parent


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(root_dir / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str
    gemini_model: str
    translate_chunk_size: int
    data_base_dir: str = "data"
    db_dir: str = "db"

    @computed_field
    @property
    def results_base_dir(self) -> Path:
        """Thư mục gốc lưu file kết quả: root/data/results/youtube"""
        return root_dir / self.data_base_dir / "youtube" / "results"

    @computed_field
    @property
    def subtitles_base_dir(self) -> Path:
        """Thư mục gốc lưu file phụ đề: root/data/subtitles/youtube"""
        return root_dir / self.data_base_dir / "youtube" / "subtitles"

    @computed_field
    @property
    def database_url(self) -> str:
        """SQLite URL trỏ đến root/db/subtitles_app.db"""
        db_folder = root_dir / self.db_dir
        os.makedirs(db_folder, exist_ok=True)
        return f"sqlite:///{db_folder / 'subtitles_app.db'}"


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()

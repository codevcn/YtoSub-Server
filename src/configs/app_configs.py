import os
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

root_dir = Path(__file__).parent.parent.parent


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(root_dir / ".env"), str(root_dir / ".gemini_key.env")],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str
    gemini_model: str
    translate_chunk_size: int
    data_dir: str = os.getenv(
        "DATA_DIR", "data"
    )  # Thư mục gốc cho dữ liệu (results, subtitles)
    db_dir: str = os.getenv("DB_DIR", "db")  # Thư mục gốc cho database (SQLite)
    translate_results_dir: str = os.getenv(
        "TRANSLATE_RESULTS_DIR", "results"
    )  # Thư mục con cho kết quả dịch
    uploaded_subtitles_dir: str = os.getenv(
        "UPLOADED_SUBTITLES_DIR", "subtitles"
    )  # Thư mục con cho phụ đề đã upload

    @computed_field
    @property
    def results_base_dir(self) -> Path:
        """Thư mục gốc lưu file kết quả: root/data/results/youtube"""
        return root_dir / self.data_dir / "youtube" / self.translate_results_dir

    @computed_field
    @property
    def subtitles_base_dir(self) -> Path:
        """Thư mục gốc lưu file phụ đề: root/data/subtitles/youtube"""
        return root_dir / self.data_dir / "youtube" / self.uploaded_subtitles_dir

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

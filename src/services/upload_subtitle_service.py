import os
from datetime import datetime
from pathlib import Path
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.configs.app_configs import AppSettings
from src.configs.roots import root_dir
from src.configs.db.models import UploadedSubtitles
from src.configs.db.utils import extract_video_id

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UploadSubtitleService:
    def __init__(self, settings: AppSettings, db: Session) -> None:
        self._base_dir: Path = settings.subtitles_base_dir
        self._db = db

    def save(
        self,
        username: str,
        video_link: str,
        is_public: bool,
        file_content: bytes,
        password: str | None = None,
    ) -> UploadedSubtitles:
        """Lưu file SRT vào đúng thư mục và ghi thông tin vào database."""
        video_id: str = extract_video_id(video_link)

        now: datetime = datetime.now()
        timestamp: str = now.strftime("%Y-%m-%d-%H")
        dir_path: Path = self._base_dir / video_id / username
        os.makedirs(dir_path, exist_ok=True)

        filename: str = f"YtoSub_subtitle_{video_id}_{timestamp}.srt"
        file_path: Path = dir_path / filename

        with open(file_path, "wb") as f:
            f.write(file_content)

        relative_path: str = str(file_path.relative_to(self._base_dir))

        password_hash: str | None = (
            _pwd_context.hash(password) if not is_public and password else None
        )

        record = UploadedSubtitles(
            username=username,
            video_id=video_id,
            video_link=video_link,
            is_public=is_public,
            password_hash=password_hash,
            file_path=relative_path,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record

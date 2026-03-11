from pathlib import Path
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.configs.app_configs import root_dir
from src.configs.db.models import UploadedSubtitles

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class GetSubtitleService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_file_path(self, record_id: int, password: str | None) -> Path:
        """Truy vấn DB, kiểm tra quyền truy cập và trả về absolute path của file SRT."""
        record: UploadedSubtitles | None = (
            self._db.query(UploadedSubtitles)
            .filter(UploadedSubtitles.id == record_id)
            .first()
        )
        print("rec:", record)

        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy file SRT với id '{record_id}'.",
            )

        if not record.is_public:
            if not password or not _pwd_context.verify(
                password, str(record.password_hash or "")
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="File yêu cầu mật khẩu, mật khẩu đã cung cấp không khớp",
                )

        file_path: Path = (root_dir / record.file_path).resolve()

        # Ngăn path traversal
        if not str(file_path).startswith(str(root_dir.resolve())):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Truy cập bị từ chối.",
            )

        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File tồn tại trong database nhưng không tìm thấy trên server.",
            )

        return file_path

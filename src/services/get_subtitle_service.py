from pathlib import Path
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

# Nhập AppSettings để lấy thông tin cấu hình thư mục dùng chung
from src.configs.app_configs import AppSettings
from src.configs.db.models import UploadedSubtitles

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class GetSubtitleService:
    def __init__(self, settings: AppSettings, db: Session) -> None:
        self._db = db
        # Thiết lập base_dir từ cấu hình để khớp với logic của UploadSubtitleService
        self._base_dir = settings.subtitles_base_dir.resolve()

    def get_file_path(self, record_id: int, password: str | None) -> Path:
        """Truy vấn DB, kiểm tra quyền truy cập và trả về absolute path của file SRT."""
        record: UploadedSubtitles | None = (
            self._db.query(UploadedSubtitles)
            .filter(UploadedSubtitles.id == record_id)
            .first()
        )

        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy file SRT với id '{record_id}'.",
            )

        # Kiểm tra quyền truy cập nếu file ở chế độ riêng tư
        if not record.is_public:
            if not password or not _pwd_context.verify(
                password, str(record.password_hash or "")
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="File yêu cầu mật khẩu, mật khẩu đã cung cấp không khớp",
                )

        # QUAN TRỌNG: Ghép với self._base_dir thay vì root_dir
        file_path: Path = (self._base_dir / record.file_path).resolve()

        # Bảo mật: Đảm bảo file_path vẫn nằm trong vùng quản lý của subtitles_base_dir
        if not file_path.is_relative_to(self._base_dir):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Truy cập bị từ chối.",
            )

        # Dùng is_file() thay vì exists() để đảm bảo không trỏ nhầm vào thư mục
        if not file_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File tồn tại trong cơ sở dữ liệu nhưng không tìm thấy trên máy chủ.",
            )

        return file_path

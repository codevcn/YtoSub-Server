from sqlalchemy.orm import Session
from src.configs.db.models import UploadedSubtitles
from src.configs.db.schemas import (
    ListSubtitlesRequest,
    ListSubtitlesResponse,
    SubtitleResponse,
)
from src.utils.constants import PAGE_SIZE


class ListSubtitlesService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(self, req: ListSubtitlesRequest) -> ListSubtitlesResponse:
        """Truy vấn cơ sở dữ liệu theo các điều kiện lọc và trả về kết quả phân trang."""

        query = self._db.query(UploadedSubtitles).filter(
            UploadedSubtitles.video_id == req.video_id
        )

        if req.username is not None:
            query = query.filter(UploadedSubtitles.username == req.username)

        if req.time_from is not None:
            query = query.filter(UploadedSubtitles.created_at >= req.time_from)

        if req.time_to is not None:
            query = query.filter(UploadedSubtitles.created_at <= req.time_to)

        # Thực thi truy vấn đếm tổng số lượng
        total: int = query.count()

        # Bước 2: Nối thêm phân trang vào câu truy vấn cơ bản và thực thi lấy dữ liệu
        records = (
            query.order_by(UploadedSubtitles.created_at.desc())
            .offset((req.page - 1) * PAGE_SIZE)
            .limit(PAGE_SIZE)
            .all()
        )

        return ListSubtitlesResponse(
            video_id=req.video_id,
            total=total,
            page=req.page,
            page_size=PAGE_SIZE,
            items=[SubtitleResponse.model_validate(r) for r in records],
        )

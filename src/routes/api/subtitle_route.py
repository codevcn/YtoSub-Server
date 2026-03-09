from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.configs.app_configs import AppSettings, get_settings
from src.configs.db.database import get_db
from src.configs.db.schemas import SubtitleResponse
from src.schemas.video_schema import ErrorResponse
from src.services.upload_subtitle_service import UploadSubtitleService

router = APIRouter(prefix="/api/v1", tags=["subtitle"])


def get_upload_subtitle_service(
    settings: AppSettings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> UploadSubtitleService:
    return UploadSubtitleService(settings=settings, db=db)


@router.post(
    "/subtitle/upload",
    response_model=SubtitleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload file phụ đề SRT",
    description=(
        "Upload file SRT lên server, lưu theo cấu trúc thư mục chuẩn và "
        "ghi thông tin vào database."
    ),
    responses={
        201: {"model": SubtitleResponse, "description": "Upload thành công"},
        400: {"model": ErrorResponse, "description": "Tham số hoặc file không hợp lệ"},
        500: {"model": ErrorResponse, "description": "Lỗi server khi xử lý file"},
    },
)
async def upload_subtitle(
    username: str = Form(
        ...,
        description="Tên người dùng (2–18 ký tự: chữ, số, gạch dưới, gạch ngang)",
        pattern="^[a-zA-Z0-9_-]{2,18}$",
    ),
    video_link: str = Form(
        ...,
        description="Đường dẫn YouTube đầy đủ (hỗ trợ youtu.be và youtube.com)",
    ),
    is_public: bool = Form(
        ...,
        description="true nếu cho phép công khai, false nếu riêng tư",
    ),
    file: UploadFile = File(..., description="File SRT cần upload"),
    service: UploadSubtitleService = Depends(get_upload_subtitle_service),
) -> SubtitleResponse:
    """
    Upload file phụ đề SRT lên server.

    - **username**: Tên người dùng, dùng để tổ chức thư mục lưu file
    - **video_link**: Đường dẫn YouTube của video tương ứng
    - **is_public**: Trạng thái công khai của phụ đề
    - **file**: File `.srt` cần upload
    """
    if not file.filename or not file.filename.lower().endswith(".srt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ chấp nhận file có định dạng .srt",
        )

    try:
        content: bytes = await file.read()
        record = service.save(
            username=username,
            video_link=video_link,
            is_public=is_public,
            file_content=content,
        )
        return record
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

from src.utils.constants import PASSWORD_MIN_LENGTH
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.configs.app_configs import AppSettings, get_settings
from src.configs.db.database import get_db
from src.configs.db.schemas import (
    GetSubtitleRequest,
    ListSubtitlesRequest,
    ListSubtitlesResponse,
    SubtitleResponse,
)
from src.schemas.video_schema import ErrorResponse
from src.services.get_subtitle_service import GetSubtitleService
from src.services.list_subtitles_service import ListSubtitlesService
from src.services.upload_subtitle_service import UploadSubtitleService
from src.utils.constants import PAGE_SIZE

router = APIRouter(prefix="/api/v1", tags=["subtitle"])


def get_upload_subtitle_service(
    settings: AppSettings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> UploadSubtitleService:
    return UploadSubtitleService(settings=settings, db=db)


def get_list_subtitles_service(
    db: Session = Depends(get_db),
) -> ListSubtitlesService:
    return ListSubtitlesService(db=db)


def get_subtitle_service(
    db: Session = Depends(get_db),
) -> GetSubtitleService:
    return GetSubtitleService(db=db)


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
        description="Tên người dùng (2-18 ký tự: chữ, số, gạch dưới, gạch ngang)",
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
    password: str | None = Form(
        None,
        description=f"Mật khẩu bảo vệ file (bắt buộc khi is_public = false, tối thiểu {PASSWORD_MIN_LENGTH} ký tự)",
        min_length=PASSWORD_MIN_LENGTH,
    ),
    file: UploadFile = File(..., description="File SRT cần upload"),
    service: UploadSubtitleService = Depends(get_upload_subtitle_service),
) -> SubtitleResponse:
    """
    Upload file phụ đề SRT lên server.

    - **username**: Tên người dùng, dùng để tổ chức thư mục lưu file
    - **video_link**: Đường dẫn YouTube của video tương ứng
    - **is_public**: Trạng thái công khai của phụ đề
    - **password**: Mật khẩu bảo vệ (bắt buộc khi `is_public = false`)
    - **file**: File `.srt` cần upload
    """
    if not is_public and not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cần cung cấp password khi is_public = false.",
        )

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
            password=password,
        )
        return record
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/subtitle/list",
    response_model=ListSubtitlesResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách file SRT đã upload",
    description=(
        "Tìm kiếm các file SRT đã upload theo video_id, username và khoảng thời gian. "
        "Kết quả được phân trang, mỗi trang 20 bản ghi, sắp xếp mới nhất trước."
    ),
    responses={
        200: {"model": ListSubtitlesResponse, "description": "Danh sách file SRT"},
        400: {"model": ErrorResponse, "description": "Tham số không hợp lệ"},
        404: {"model": ErrorResponse, "description": "Không tìm thấy kết quả nào"},
    },
)
async def list_subtitles(
    body: ListSubtitlesRequest,
    service: ListSubtitlesService = Depends(get_list_subtitles_service),
) -> ListSubtitlesResponse:
    """
    Lấy danh sách các file SRT đã upload, hỗ trợ lọc và phân trang.

    - **video_id**: ID video YouTube (bắt buộc)
    - **username**: Lọc theo tên người dùng (tuỳ chọn)
    - **time_from**: Lọc từ thời điểm, ISO 8601 (tuỳ chọn, VD: `2026-03-01T00:00:00`)
    - **time_to**: Lọc đến thời điểm, ISO 8601 (tuỳ chọn)
    - **page**: Số trang, bắt đầu từ 1 (bắt buộc)
    """
    result: ListSubtitlesResponse = service.list(body)
    if not result.items:
        return ListSubtitlesResponse(
            items=[],
            total=0,
            page=body.page,
            page_size=PAGE_SIZE,
            video_id=body.video_id,
        )
    return result


@router.post(
    "/subtitle/content",
    status_code=status.HTTP_200_OK,
    summary="Lấy nội dung file SRT",
    description=(
        "Trả về nội dung file SRT dạng stream. "
        "Nếu file là riêng tư (is_public = false), bắt buộc phải cung cấp đúng password."
    ),
    responses={
        200: {"description": "Nội dung file SRT (text/plain; charset=utf-8)"},
        403: {
            "model": ErrorResponse,
            "description": "Mật khẩu không khớp hoặc truy cập bị từ chối",
        },
        404: {
            "model": ErrorResponse,
            "description": "Không tìm thấy bản ghi hoặc file",
        },
    },
)
async def get_subtitle_content(
    body: GetSubtitleRequest,
    service: GetSubtitleService = Depends(get_subtitle_service),
) -> StreamingResponse:
    """
    Lấy nội dung file SRT theo id bản ghi trong database.

    - **id**: ID bản ghi trong database
    - **password**: Mật khẩu bảo vệ (bắt buộc nếu file là riêng tư)
    """
    file_path = service.get_file_path(body.id, body.password)

    def iter_file():
        with open(file_path, "rb") as f:
            yield from f

    return StreamingResponse(
        iter_file(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{file_path.name}"',
        },
    )

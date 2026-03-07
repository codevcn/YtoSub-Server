from fastapi import APIRouter, Depends, HTTPException, status
from src.configs.app_configs import AppSettings, get_settings
from src.schemas.video_schema import (
    ErrorResponse,
    TranslateVideoRequest,
    TranslateVideoResponse,
)
from src.services.process_video_service import ProcessVideoService

router = APIRouter(prefix="/api/v1", tags=["video"])


def get_process_video_service(
    settings: AppSettings = Depends(get_settings),
) -> ProcessVideoService:
    return ProcessVideoService(settings=settings)


@router.post(
    "/video/translate",
    response_model=TranslateVideoResponse,
    status_code=status.HTTP_200_OK,
    summary="Dịch phụ đề YouTube sang tiếng Việt",
    description=(
        "Tải phụ đề tiếng Anh từ video YouTube, dịch sang tiếng Việt bằng Gemini AI "
        "và lưu kết quả thành file SRT."
    ),
    responses={
        200: {"model": TranslateVideoResponse, "description": "Dịch thành công"},
        400: {
            "model": ErrorResponse,
            "description": "URL không hợp lệ hoặc thiếu tham số",
        },
        404: {"model": ErrorResponse, "description": "Không tìm thấy phụ đề cho video"},
        500: {"model": ErrorResponse, "description": "Lỗi server trong quá trình dịch"},
    },
)
async def translate_video(
    request: TranslateVideoRequest,
    service: ProcessVideoService = Depends(get_process_video_service),
) -> TranslateVideoResponse:
    """
    Dịch phụ đề video YouTube từ tiếng Anh sang tiếng Việt.

    - **video_url**: Đường dẫn YouTube đầy đủ (hỗ trợ `youtu.be` và `youtube.com`)
    - **video_summary**: Tóm tắt nội dung video (tuỳ chọn) để cải thiện chất lượng dịch
    """
    try:
        return service.process_video(
            video_url=request.video_url,
            video_summary=request.video_summary,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

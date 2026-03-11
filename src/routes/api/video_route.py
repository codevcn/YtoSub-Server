from src.managers.sse_manager import sse_manager
import asyncio
import json
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Query,
    Request,
    status,
    HTTPException,
)
from sse_starlette.sse import EventSourceResponse
from src.configs.app_configs import AppSettings, get_settings
from src.schemas.video_schema import (
    ErrorResponse,
    TranslateAcceptedResponse,
    TranslateVideoRequest,
)
from src.services.process_video_service import ProcessVideoService

router = APIRouter(prefix="/api/v1", tags=["video"])


def get_process_video_service(
    settings: AppSettings = Depends(get_settings),
) -> ProcessVideoService:
    return ProcessVideoService(settings=settings)


@router.post(
    "/video/translate",
    response_model=TranslateAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Bắt đầu dịch phụ đề YouTube",
    description=(
        "Tiếp nhận yêu cầu dịch phụ đề và xử lý nền. "
        "Kết nối tới endpoint /video/sse để nhận tiến độ theo thời gian thực."
    ),
    responses={
        202: {
            "model": TranslateAcceptedResponse,
            "description": "Yêu cầu đã được tiếp nhận",
        },
        400: {
            "model": ErrorResponse,
            "description": "URL không hợp lệ hoặc thiếu tham số",
        },
        500: {
            "model": ErrorResponse,
            "description": "Lỗi server trong quá trình xử lý",
        },
    },
)
async def translate_video(
    body: TranslateVideoRequest,
    background_tasks: BackgroundTasks,
    service: ProcessVideoService = Depends(get_process_video_service),
) -> TranslateAcceptedResponse:
    """
    Bắt đầu quá trình dịch phụ đề video YouTube từ tiếng Anh sang tiếng Việt.
    Kết quả sẽ được stream về client qua kết nối SSE tại /video/sse.

    - **username**: Tên người dùng, dùng để tổ chức thư mục lưu file SRT
    - **video_url**: Đường dẫn YouTube đầy đủ (hỗ trợ `youtu.be` và `youtube.com`)
    - **video_summary**: Tóm tắt nội dung video (tuỳ chọn) để cải thiện chất lượng dịch
    """

    # 1. Trích xuất video_id từ URL để tạo task_id duy nhất
    try:
        # Giả định bạn đã thêm hàm _get_video_by_link_service() vào ProcessVideoService
        # theo như đề xuất ở phần trước, hoặc bạn có thể gọi trực tiếp hàm extract_video_id
        # nếu bạn đã đưa nó ra ngoài thành một hàm tiện ích chung.
        video_id = service._get_video_by_link_service().extract_video_id(body.video_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Tạo khóa định danh duy nhất cho tiến trình này
    task_id = f"{body.username}:{video_id}"

    # 2. Đưa tác vụ vào chạy nền
    # Lưu ý: Sử dụng stream_process_video thay vì process_video_by_link
    # và truyền task_id thay vì progress_queue
    background_tasks.add_task(
        service.process_video_by_link,
        video_url=body.video_url,
        username=body.username,
        video_summary=body.video_summary,
        task_id=task_id,
    )

    return TranslateAcceptedResponse(
        message=(
            f"Yêu cầu dịch phụ đề đã được tiếp nhận. "
            f"Kết nối SSE tại /api/v1/video/sse?username={body.username}&video_id={video_id} để theo dõi tiến độ."
        )
    )


@router.get("/video/sse")
async def connect_sse(
    request: Request,
    username: str = Query(...),
    video_id: str = Query(..., description="ID của video trên YouTube"),
) -> EventSourceResponse:

    task_id = f"{username}:{video_id}"
    queue = await sse_manager.subscribe(task_id)
    print(f"Đã thiết lập SSE với client {username} cho video {video_id}.")

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event: dict = await asyncio.wait_for(queue.get(), timeout=1.0)
                    print(
                        f"Đang gửi sự kiện tới client {username} cho video {video_id}: {event['event']}"
                    )
                    yield {
                        "event": event["event"],
                        "data": json.dumps(event["data"], ensure_ascii=False),
                    }
                    if event["event"] in ("done", "error"):
                        break
                except asyncio.TimeoutError:
                    continue
        finally:
            # Xóa Queue của client này khi họ ngắt kết nối
            sse_manager.unsubscribe(task_id, queue)
            print(f"Đã ngắt kết nối client {username} cho video {video_id}.")

    return EventSourceResponse(event_generator())

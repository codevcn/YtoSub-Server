from datetime import datetime, timezone
from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["health"])


class HealthCheckResponse(BaseModel):
    status: str
    message: str
    # Thay đổi str thành datetime để Pydantic tự động format
    timestamp: datetime


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Kiểm tra trạng thái hoạt động của server",
    description="Endpoint đơn giản để kiểm tra xem API server có đang hoạt động hay không.",
    responses={
        200: {
            "model": HealthCheckResponse,
            "description": "Server đang hoạt động bình thường",
        },
    },
)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint để monitoring và load balancer kiểm tra trạng thái server.

    Trả về:
    - **status**: "ok" nếu server đang chạy
    - **message**: Thông báo xác nhận
    - **timestamp**: Thời gian thực hiện request theo chuẩn UTC
    """
    return HealthCheckResponse(
        status="ok",
        message="YtoSub Server đang hoạt động bình thường",
        # Lấy thời gian hiện tại theo chuẩn UTC
        timestamp=datetime.now(timezone.utc),
    )

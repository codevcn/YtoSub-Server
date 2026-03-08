from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from src.configs.app_configs import AppSettings, get_settings
from src.schemas.video_schema import (
    DownloadFileRequest,
    ErrorResponse,
    ListFilesRequest,
    ListFilesResponse,
    SrtFileInfo,
)
from src.services.download_file_service import DownloadFileService

router = APIRouter(prefix="/api/v1", tags=["file"])


def get_download_service(
    settings: AppSettings = Depends(get_settings),
) -> DownloadFileService:
    return DownloadFileService(settings=settings)


@router.post(
    "/file/download",
    summary="Tải xuống file kết quả",
    description="Tải xuống file SRT dịch, tóm tắt (summary) hoặc transcript gốc.",
    responses={
        200: {"description": "File được trả về thành công"},
        400: {"model": ErrorResponse, "description": "Tham số không hợp lệ"},
        403: {"model": ErrorResponse, "description": "Truy cập bị từ chối"},
        404: {"model": ErrorResponse, "description": "File không tồn tại"},
    },
    status_code=status.HTTP_200_OK,
)
async def download_file(
    body: DownloadFileRequest,
    service: DownloadFileService = Depends(get_download_service),
) -> FileResponse:
    """
    Tải xuống file kết quả dịch phụ đề.

    - **username**: Tên người dùng
    - **video_id**: ID video YouTube
    - **filename**: Tên file cần tải (VD: `YtoSub_abc123_2026-03-08-10.srt`)
    """
    file_path = service.resolve_file_path(body.username, body.video_id, body.filename)
    return FileResponse(path=str(file_path), filename=body.filename)


@router.post(
    "/file/list",
    response_model=ListFilesResponse,
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách file SRT của người dùng",
    description="Trả về danh sách tất cả các file SRT đã dịch thuộc về username được cung cấp.",
    responses={
        200: {"model": ListFilesResponse, "description": "Danh sách file SRT"},
        400: {"model": ErrorResponse, "description": "Username không hợp lệ"},
        404: {"model": ErrorResponse, "description": "Không tìm thấy file SRT nào"},
    },
)
async def list_files(
    body: ListFilesRequest,
    service: DownloadFileService = Depends(get_download_service),
) -> ListFilesResponse:
    """
    Lấy danh sách tất cả file SRT đã dịch của một người dùng.

    - **username**: Tên người dùng cần tra cứu
    """
    files = service.list_srt_files(body.username)
    if not files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy file SRT nào cho người dùng '{body.username}'.",
        )
    return ListFilesResponse(
        username=body.username,
        files=[SrtFileInfo(**f) for f in files],
    )

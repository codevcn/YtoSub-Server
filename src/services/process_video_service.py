from src.managers.sse_manager import sse_manager
import asyncio
from importlib import import_module
from src.configs.app_configs import AppSettings
from src.schemas.video_schema import TranslateVideoResponse
from src.services.process_video_by_link_service import ProcessVideoByLinkService
from youtube_transcript_api._transcripts import FetchedTranscript

# srt-storage-service.py dùng kebab-case theo quy định dự án, phải import qua importlib
_srt_storage_module = import_module("src.services.srt-storage-service")
SrtStorageService = _srt_storage_module.SrtStorageService


class ProcessVideoService:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    # Hàm hỗ trợ lấy instance của service bên dưới để route có thể trích xuất video_id
    def _get_video_by_link_service(self):
        return ProcessVideoByLinkService(settings=self._settings)

    async def process_video_by_link(
        self, video_url: str, username: str, video_summary: str | None, task_id: str
    ) -> None:
        print(
            f"[ProcessVideo] Bắt đầu xử lý video: {video_url} cho user: {username} với task_id: {task_id}"
        )
        sse_manager.push_event(
            task_id,
            "start",
            {"message": "Đang bắt đầu xử lý video...", "percent": 1},
        )

        service = ProcessVideoByLinkService(settings=self._settings)
        loop = asyncio.get_running_loop()

        try:
            video_id: str = service.extract_video_id(video_url)
            data: FetchedTranscript | None = await asyncio.to_thread(
                service.get_youtube_subtitle, video_id
            )
            sse_manager.push_event(
                task_id,
                "progress",
                {
                    "message": "Đã trích xuất phụ đề gốc từ YouTube",
                    "percent": 10,
                },
            )

            if not data:
                sse_manager.push_event(
                    task_id, "error", {"message": f"Không tìm thấy phụ đề: {video_id}"}
                )
                return

            storage = SrtStorageService(settings=self._settings)
            output_path: str = storage.generate_path(video_id, username)

            await asyncio.to_thread(
                service.process_and_save_srt,
                data,
                output_path,
                video_url,
                video_summary,
                task_id,
                loop,
            )

            sse_manager.push_event(
                task_id,
                "done",
                {
                    "video_id": video_id,
                    "output_file": output_path,
                    "message": f"Hoàn thành dịch phụ đề! File '{output_path}' đã sẵn sàng.",
                    "percent": 100,
                },
            )
        except Exception as e:
            sse_manager.push_event(task_id, "error", {"message": str(e)})

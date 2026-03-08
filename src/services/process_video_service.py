from src.managers.sse_manager import sse_manager
import asyncio
from src.configs.app_configs import AppSettings
from src.services.process_video_by_link_service import ProcessVideoByLinkService
from youtube_transcript_api._transcripts import FetchedTranscript
from src.services.translate_storage_service import (
    TranslateStorageService,
    TranscriptStorageService,
    SummaryStorageService,
)


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

            if not data:
                sse_manager.push_event(
                    task_id, "error", {"message": f"Không tìm thấy phụ đề: {video_id}"}
                )
                return

            sse_manager.push_event(
                task_id,
                "progress",
                {
                    "message": "Đã trích xuất phụ đề gốc từ YouTube",
                    "percent": 10,
                },
            )

            # Lưu transcript gốc ra file
            transcript_storage = TranscriptStorageService(settings=self._settings)
            transcript_content = "\n".join(
                f"[{int(item.start // 3600):02}:{int((item.start % 3600) // 60):02}:{int(item.start % 60):02}] {item.text}"
                for item in data
            )
            await asyncio.to_thread(
                transcript_storage.save, transcript_content, video_id, username
            )
            print(f"[ProcessVideo] Đã lưu transcript gốc cho video: {video_id}")
            _, transcript_filename = transcript_storage.generate_path(
                video_id, username
            )

            translate_storage = TranslateStorageService(settings=self._settings)
            translate_path, translate_filename = translate_storage.generate_path(
                video_id, username
            )
            summary_storage = SummaryStorageService(settings=self._settings)
            _, summary_filename = summary_storage.generate_path(video_id, username)

            await asyncio.to_thread(
                service.process_and_save_srt,
                data,
                translate_path,
                video_url,
                video_summary,
                task_id,
                loop,
                summary_storage,
                video_id,
                username,
            )

            sse_manager.push_event(
                task_id,
                "done",
                {
                    "video_id": video_id,
                    "translate_file": translate_filename,
                    "summary_file": summary_filename,
                    "transcript_file": transcript_filename,
                    "message": f"Hoàn thành dịch phụ đề! File '{translate_filename}' đã sẵn sàng.",
                    "percent": 100,
                },
            )
        except Exception as e:
            sse_manager.push_event(task_id, "error", {"message": str(e)})

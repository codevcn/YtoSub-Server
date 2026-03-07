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

    def process_video(
        self, video_url: str, username: str, video_summary: str | None = None
    ) -> TranslateVideoResponse:
        service = ProcessVideoByLinkService(settings=self._settings)

        try:
            video_id: str = service.extract_video_id(video_url)
            print(f"Đã trích xuất thành công Video ID: {video_id}")
        except ValueError as e:
            raise ValueError(f"URL YouTube không hợp lệ: {e}") from e

        data: FetchedTranscript | None = service.get_youtube_subtitle(video_id)
        if not data:
            raise FileNotFoundError(
                f"Không tìm thấy phụ đề tiếng Anh cho video: {video_id}"
            )

        storage = SrtStorageService(settings=self._settings)
        output_path: str = storage.generate_path(video_id, username)

        service.process_and_save_srt(
            data,
            filename=output_path,
            youtube_video_link=video_url,
            video_summary=video_summary,
        )

        return TranslateVideoResponse(
            video_id=video_id,
            output_file=output_path,
            message=f"Hoàn thành! File '{output_path}' đã sẵn sàng.",
        )

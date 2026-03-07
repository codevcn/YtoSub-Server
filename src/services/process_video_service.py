import os
from src.configs.app_configs import AppSettings, root_dir
from src.schemas.video_schema import TranslateVideoResponse
from src.services.process_video_by_link_service import ProcessVideoByLinkService
from youtube_transcript_api._transcripts import FetchedTranscript


class ProcessVideoService:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    def process_video(
        self, video_url: str, video_summary: str | None = None
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

        output_dir = os.path.join(root_dir, "result")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"vietsub_{video_id}.srt")

        service.process_and_save_srt(
            data,
            filename=output_path,
            youtube_video_link=video_url,
            video_summary=video_summary,
        )

        return TranslateVideoResponse(
            video_id=video_id,
            output_file=output_path,
            message=f"Hoàn thành! File 'vietsub_{video_id}.srt' đã sẵn sàng.",
        )

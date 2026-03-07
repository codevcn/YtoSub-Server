from src.managers.sse_manager import sse_manager
import asyncio
import json
import re
import time
from urllib.parse import parse_qs, urlparse
from google import genai
from google.genai import types
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._transcripts import FetchedTranscript
from src.configs.app_configs import AppSettings


class ProcessVideoByLinkService:
    def __init__(self, settings: AppSettings) -> None:
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._gemini_model: str = settings.gemini_model
        self._translate_chunk_size: int = settings.translate_chunk_size

    def get_youtube_subtitle(self, video_id: str) -> FetchedTranscript | None:
        """Tải phụ đề tiếng Anh từ YouTube."""
        try:
            print("[ProcessVideo] Đang tải phụ đề gốc...")
            api = YouTubeTranscriptApi()
            transcript = api.fetch(video_id, languages=["en"])
            return transcript
        except Exception as e:
            print(f"[ProcessVideo] Lỗi khi tải phụ đề: {e}")
            return None

    def format_time(self, seconds: float) -> str:
        """Chuyển đổi giây sang định dạng thời gian chuẩn của SRT."""
        td = float(seconds)
        hours = int(td // 3600)
        minutes = int((td % 3600) // 60)
        secs = int(td % 60)
        millis = int((td % 1) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

    def load_summary(self, youtube_video_link: str) -> str | None:
        """Yêu cầu Gemini tóm tắt phim."""
        prompt = f"""
        Bạn hãy tóm tắt nội dung của video YouTube tại đường dẫn sau: {youtube_video_link}
        
        Vui lòng trả về kết quả theo đúng định dạng dưới đây:
        - Title:
        - Genre:
        - Main Characters:
        - Theme:
        - Summary (theo video timeline): (viết thành từng đoạn văn, các đoạn văn có thứ tự nối tiếp nhau dựa trên trình tự thời gian của video)
        """

        try:
            print(
                f"[ProcessVideo] Đang gửi yêu cầu tóm tắt video {youtube_video_link} đến Gemini..."
            )

            # Gọi API để tạo nội dung tóm tắt
            response = self._client.models.generate_content(
                model=self._gemini_model, contents=prompt
            )

            # Kiểm tra xem API có trả về văn bản hợp lệ hay không
            summary_text: str | None = response.text
            if summary_text:
                print("[ProcessVideo] Đã nhận được bản tóm tắt từ Gemini thành công.")
                return summary_text
            else:
                print(
                    "Lỗi: Nhận được phản hồi nhưng không có nội dung văn bản từ Gemini."
                )
                return None

        except Exception as e:
            # Bắt mọi lỗi xảy ra trong quá trình kết nối hoặc xử lý của API
            print(
                f"[ProcessVideo] Đã xảy ra lỗi trong quá trình gọi API để tóm tắt video: {e}"
            )
            return None

    def translate_chunk(
        self, chunk_data: list, summary: str | None = None, max_retries: int = 3
    ) -> list | None:
        """Dịch một cụm nhỏ phụ đề, không dùng lịch sử chat để tránh tràn token."""
        payload: list[dict] = [
            {"id": i, "text": item.text} for i, item in enumerate(chunk_data)
        ]

        # Ghép bản tóm tắt trực tiếp vào ngữ cảnh của câu lệnh
        context_text: str = (
            f"Tóm tắt phim (dùng để tham khảo bối cảnh phim):\n{summary}\n\n"
            if summary
            else ""
        )

        translate_prompt = f"""
        Bạn là một chuyên gia dịch thuật phim ảnh. {context_text}
        Yêu cầu:
        1. Hãy dịch các dòng phụ đề sau từ tiếng Anh sang tiếng Việt.
        2. Giữ nguyên văn phong tự nhiên, sát với ngữ cảnh giao tiếp.
        3. Bạn TUYỆT ĐỐI KHÔNG thêm bất kỳ bình luận nào.
        4. Trả về đúng định dạng JSON array ban đầu, chỉ thay đổi nội dung bên trong trường "text" thành tiếng Việt.
        
        Dữ liệu cần dịch:
        {json.dumps(payload, ensure_ascii=False)}
        """

        for attempt in range(1, max_retries + 1):
            try:
                # Gọi API dạng stateless (không lưu lịch sử) thay vì dùng chat
                response = self._client.models.generate_content(
                    model=self._gemini_model,
                    contents=translate_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    ),
                )

                if response.text is None:
                    raise ValueError("API trả về phản hồi rỗng.")
                result: list = json.loads(response.text)
                if len(result) != len(chunk_data):
                    raise ValueError(
                        f"Số dòng trả về ({len(result)}) không khớp ({len(chunk_data)})."
                    )
                return result
            except Exception as e:
                err_str: str = str(e)
                print(f"[ProcessVideo]   Lần thử {attempt}/{max_retries} thất bại: {e}")

                # Nếu model không có free tier (limit: 0), không cần retry thêm
                if "limit: 0" in err_str:
                    print(
                        "  Model không có free tier hoặc quota đã hết hoàn toàn. Vui lòng đổi model hoặc nâng cấp plan."
                    )
                    return None

                if attempt < max_retries:
                    # Đọc thời gian chờ (retryDelay) từ phản hồi lỗi nếu có (ví dụ: 'Please retry in 56s')
                    match = re.search(
                        r"retry[\w\s]*in[\s]+(\d+)", err_str, re.IGNORECASE
                    )
                    wait: int = int(match.group(1)) + 5 if match else 65 * attempt
                    print(f"[ProcessVideo]   Chờ {wait}s trước khi thử lại...")
                    time.sleep(wait)

        return None

    def _push_event(
        self, loop: asyncio.AbstractEventLoop, task_id: str, event_type: str, data: dict
    ) -> None:
        """Sử dụng loop chính để gọi hàm push_event của Manager một cách an toàn từ luồng phụ."""
        loop.call_soon_threadsafe(sse_manager.push_event, task_id, event_type, data)

    def process_and_save_srt(
        self,
        original_data: FetchedTranscript,
        filename: str,
        youtube_video_link: str,
        video_summary: str | None = None,
        task_id: str | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        """Xử lý chia nhỏ dữ liệu, dịch và lưu thành file SRT."""
        translated_subtitles: list = []

        summary: str | None = video_summary or self.load_summary(youtube_video_link)
        if summary:
            print(
                "Đã tải bản tóm tắt phim. Sẽ dùng bản tóm tắt làm ngữ cảnh cho từng cụm."
            )
        else:
            print(
                "[ProcessVideo] Không có bản tóm tắt phim. Sẽ dịch mà không có ngữ cảnh phim."
            )

        total_lines: int = len(original_data)
        total_chunks: int = (
            total_lines + self._translate_chunk_size - 1
        ) // self._translate_chunk_size
        snippets: list = list(original_data)
        print(
            f"[ProcessVideo] Tổng cộng có {total_lines} dòng phụ đề. Bắt đầu quá trình dịch..."
        )

        # Cập nhật: Sử dụng task_id thay cho progress_queue
        if task_id and loop:
            self._push_event(
                loop,
                task_id,
                "progress",
                {
                    "message": "Đang bắt đầu dịch phụ đề...",
                    "total_lines": total_lines,
                    "total_chunks": total_chunks,
                    "percent": 20,
                },
            )

        for i in range(0, total_lines, self._translate_chunk_size):
            chunk: list = snippets[i : i + self._translate_chunk_size]
            print(
                f"Đang xử lý dòng {i + 1} đến {min(i + self._translate_chunk_size, total_lines)}..."
            )

            # Truyền trực tiếp summary vào hàm dịch
            translated_chunk = self.translate_chunk(chunk, summary)

            # Kiểm tra tính hợp lệ của dữ liệu trả về
            if translated_chunk:
                translated_subtitles.extend(translated_chunk)
            else:
                # Tính toán lại số thứ tự đúng của Chunk
                chunk_index = (i // self._translate_chunk_size) + 1
                print(
                    f"Cảnh báo: Chunk {chunk_index} thất bại trong quá trình dịch. Giữ nguyên tiếng Anh cho đoạn này."
                )
                # Fallback: Nếu AI trả về lỗi, giữ nguyên bản gốc để không làm hỏng file
                fallback_chunk: list[dict] = [{"text": item.text} for item in chunk]
                translated_subtitles.extend(fallback_chunk)

            # Cập nhật: Gửi tiến độ qua SSE sử dụng task_id
            if task_id and loop:
                chunks_done: int = i // self._translate_chunk_size + 1
                lines_done: int = min(i + self._translate_chunk_size, total_lines)

                # Tính toán phần trăm: Bắt đầu từ mốc 20%, phần dịch thuật chiếm 70% còn lại
                current_percent = (
                    int(20 + (lines_done / total_lines * 70)) if total_lines > 0 else 20
                )

                self._push_event(
                    loop,
                    task_id,
                    "progress",
                    {
                        "message": f"Đã dịch xong {lines_done}/{total_lines} dòng phụ đề.",
                        "chunk_index": chunks_done,
                        "total_chunks": total_chunks,
                        "lines_done": lines_done,
                        "total_lines": total_lines,
                        "percent": current_percent,
                    },
                )

            # Tạm nghỉ 4 giây giữa các lần gọi để đảm bảo an toàn cho gói miễn phí (tránh vượt rate limit)
            time.sleep(4)

        # Ghi dữ liệu ra file SRT
        if task_id and loop:
            self._push_event(
                loop,
                task_id,
                "progress",
                {
                    "video_id": youtube_video_link,
                    "output_file": filename,
                    "message": "Đang định dạng và lưu file SRT...",
                    "percent": 90,
                },
            )
        print("[ProcessVideo] Đang định dạng và lưu file SRT...")
        with open(filename, "w", encoding="utf-8") as f:
            # Sử dụng hàm zip để ráp thời gian gốc và văn bản đã dịch một cách chính xác
            for index, (orig, trans) in enumerate(
                zip(original_data, translated_subtitles)
            ):
                start_time: str = self.format_time(orig.start)
                end_time: str = self.format_time(orig.start + orig.duration)
                translated_text: str = trans.get("text", orig.text)

                f.write(
                    f"{index + 1}\n{start_time} --> {end_time}\n{translated_text}\n\n"
                )

        print(f"[ProcessVideo] Hoàn thành! File '{filename}' đã sẵn sàng.")

    def extract_video_id(self, url: str) -> str:
        """Trích xuất Video ID từ nhiều định dạng đường dẫn YouTube khác nhau."""
        # Loại bỏ dấu nháy đơn/kép bao quanh URL (thường do đọc từ file config)
        url = url.strip().strip("\"'")
        parsed = urlparse(url)
        if parsed.hostname == "youtu.be":
            # Hỗ trợ: https://youtu.be/EKgy5EM-Vhw?si=xxx
            return parsed.path.lstrip("/")
        if parsed.hostname in ("www.youtube.com", "youtube.com"):
            if parsed.path == "/watch":
                # Hỗ trợ: https://www.youtube.com/watch?v=EKgy5EM-Vhw
                query_params = parse_qs(parsed.query)
                video_id = query_params.get("v", [None])[0]
                if video_id:
                    return video_id
                raise ValueError(
                    f"Không tìm thấy tham số 'v' chứa Video ID trong URL: {url}"
                )
            if parsed.path.startswith("/embed/"):
                return parsed.path.split("/")[2]
        raise ValueError(f"Không nhận ra URL YouTube: {url}")

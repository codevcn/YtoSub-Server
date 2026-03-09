import re
from pathlib import Path


def extract_video_id(url: str) -> str:
    """Trích xuất ID từ link Youtube: watch?v=ID hoặc youtu.be/ID"""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise ValueError("Link YouTube không hợp lệ")


def get_upload_path(video_id: str, username: str) -> Path:
    """Tạo folder theo cấu trúc: data/youtube/subtitles/{video_id}/{username}/"""
    path = Path(f"data/youtube/subtitles/{video_id}/{username}")
    path.mkdir(parents=True, exist_ok=True)
    return path

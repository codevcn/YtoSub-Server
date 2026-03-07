from pydantic import BaseModel


class TranslateVideoRequest(BaseModel):
    video_url: str
    video_summary: str | None = None


class TranslateVideoResponse(BaseModel):
    video_id: str
    output_file: str
    message: str


class ErrorResponse(BaseModel):
    detail: str

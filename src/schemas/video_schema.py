from pydantic import BaseModel, Field


class TranslateVideoRequest(BaseModel):
    username: str = Field(
        ...,
        description="Tên người dùng, dùng để tổ chức thư mục lưu file SRT",
        pattern="^[a-zA-Z0-9_-]{2,18}$",
    )
    video_url: str
    video_summary: str | None = None


class TranslateVideoResponse(BaseModel):
    video_id: str
    output_file: str
    message: str


class ErrorResponse(BaseModel):
    detail: str


class TranslateAcceptedResponse(BaseModel):
    message: str

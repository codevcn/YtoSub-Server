from pydantic import BaseModel, Field
from datetime import datetime


class SubtitleBase(BaseModel):
    username: str
    video_link: str
    is_public: bool


class SubtitleResponse(SubtitleBase):
    id: int
    video_id: str
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True


class ListSubtitlesRequest(BaseModel):
    video_id: str = Field(..., description="ID video YouTube (bắt buộc)")
    username: str | None = Field(None, description="Lọc theo tên người dùng")
    time_from: datetime | None = Field(
        None, description="Lọc từ thời điểm (ISO 8601, tuỳ chọn)"
    )
    time_to: datetime | None = Field(
        None, description="Lọc đến thời điểm (ISO 8601, tuỳ chọn)"
    )
    page: int = Field(1, ge=1, description="Số trang (bắt đầu từ 1)")


class ListSubtitlesResponse(BaseModel):
    video_id: str
    total: int
    page: int
    page_size: int
    items: list[SubtitleResponse]


class GetSubtitleRequest(BaseModel):
    id: int = Field(..., description="ID bản ghi trong database")
    password: str | None = Field(None, description="Mật khẩu (bắt buộc nếu file là riêng tư)")

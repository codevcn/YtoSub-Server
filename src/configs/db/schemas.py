from pydantic import BaseModel
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

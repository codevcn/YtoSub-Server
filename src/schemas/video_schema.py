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


class DownloadFileRequest(BaseModel):
    username: str = Field(
        ...,
        description="Tên người dùng",
        pattern="^[a-zA-Z0-9_-]{2,18}$",
    )
    video_id: str = Field(..., description="ID video YouTube")
    filename: str = Field(..., description="Tên file cần tải (VD: YtoSub_abc123_2026-03-08-10.srt)")


class ListFilesRequest(BaseModel):
    username: str = Field(
        ...,
        description="Tên người dùng cần tra cứu",
        pattern="^[a-zA-Z0-9_-]{2,18}$",
    )


class SrtFileInfo(BaseModel):
    video_id: str = Field(..., description="ID video YouTube")
    filename: str = Field(..., description="Tên file SRT")


class ListFilesResponse(BaseModel):
    username: str
    files: list[SrtFileInfo]

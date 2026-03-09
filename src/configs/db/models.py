from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from .database import Base


# Uploaded Subtitles model
class UploadedSubtitles(Base):
    __tablename__ = "uploaded_subtitles"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    video_id = Column(String, index=True)
    video_link = Column(String)
    is_public = Column(Boolean, default=True)
    file_path = Column(String)  # Đường dẫn đến file trên server
    created_at = Column(DateTime, default=datetime.now)

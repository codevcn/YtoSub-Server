from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.routes.api.video_route import router as video_router
from src.routes.api.file_route import router as file_router
from src.routes.api.subtitle_route import router as subtitle_router
from src.routes.api.health_route import router as health_router
from src.configs.db.database import Base, engine
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

load_dotenv(dotenv_path=".env")
load_dotenv(dotenv_path=".gemini_key.env")
print(
    "Environment variables loaded successfully:",
    os.getenv("GEMINI_API_KEY"),
)


# Quản lý vòng đời của ứng dụng FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo các bảng cơ sở dữ liệu khi ứng dụng bắt đầu khởi chạy
    Base.metadata.create_all(bind=engine)
    yield
    # Có thể thêm các tác vụ dọn dẹp khi ứng dụng tắt tại đây


# Giả sử bạn lấy danh sách origins từ biến môi trường,
# nếu không có thì mặc định dùng localhost để dev.
ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "").split(", ")
print(f"Allowed origins: {ALLOWED_ORIGINS}")

app = FastAPI(
    title="YtoSub Server",
    description="API dịch phụ đề YouTube từ tiếng Anh sang tiếng Việt bằng Gemini AI.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Sử dụng danh sách đã cấu hình
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Hạn chế các method cần thiết
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(video_router)
app.include_router(file_router)
app.include_router(subtitle_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code, content={"message": str(exc.detail)}
    )

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.routes.api.video_route import router as video_router
from src.routes.api.file_route import router as file_router
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

# Giả sử bạn lấy danh sách origins từ biến môi trường,
# nếu không có thì mặc định dùng localhost để dev.
ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "").split(", ")
print(f"Allowed origins: {ALLOWED_ORIGINS}")

app = FastAPI(
    title="YtoSub Server",
    description="API dịch phụ đề YouTube từ tiếng Anh sang tiếng Việt bằng Gemini AI.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Sử dụng danh sách đã cấu hình
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Hạn chế các method cần thiết
    allow_headers=["*"],
)
app.include_router(video_router)
app.include_router(file_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code, content={"message": str(exc.detail)}
    )

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.routes.api.video_route import router as video_router

app = FastAPI(
    title="YtoSub Server",
    description="API dịch phụ đề YouTube từ tiếng Anh sang tiếng Việt bằng Gemini AI.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(video_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"message": f"Route '{request.url.path}' không tồn tại."},
        )
    return JSONResponse(status_code=exc.status_code, content={"message": str(exc.detail)})

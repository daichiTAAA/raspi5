# {
#   "camera_id": "cam1",
#   "rtsp_url": "rtsp://192.168.0.101:8554/stream1"
# }

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles

# from fastapi.middleware.cors import CORSMiddleware

from api.routers import camera
from api.setup_logger import setup_logger
from api.db import async_engine, Base

logger, log_decorator = setup_logger(__name__)


# データベースの初期化
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup event")
    async with async_engine.begin() as conn:
        logger.info("Creating tables...")
        # 全てのテーブルを削除する。開発用。
        await conn.run_sync(Base.metadata.drop_all)
        # Baseを継承したモデルクラスに対応するテーブルを作成する。
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created.")
    yield
    logger.info("shutdown event")


app = FastAPI(lifespan=lifespan)
port: int = 8100

# origins = [
#     "http://localhost",
#     "http://localhost:8100",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Mounted static directory")
except Exception as e:
    logger.error(f"Error mounting static directory: {e}")


app.include_router(camera.router_v1, prefix="/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to the Japan Tourism Info API"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info", reload=True)

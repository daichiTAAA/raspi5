from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles

from api.routers import camera, camera_instance
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
port: int = 8200

try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Mounted static directory")
except Exception as e:
    logger.error(f"Error mounting static directory: {e}")


app.include_router(camera.router_v1, prefix="/v1")
app.include_router(camera_instance.router_v1, prefix="/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to the Japan Tourism Info API"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info", reload=True)

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi

from api.routers import usercamera, usercamera_instance, wss
from api.setup_logger import setup_logger
from api.get_env import env_info
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


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Video API",
        version="1.0.0",
        description="API documentation for Video",
        routes=app.routes,
    )
    # 自動的にSwaggerUIにWebSocketエンドポイントが表示されないため、
    # WebSocketエンドポイントを手動で追加
    openapi_schema["paths"]["/v1/wsss/ws/{user_id}/{camera_id}"] = {
        "get": {
            "summary": "WebSocket connection",
            "description": (
                "WebSocket connection for user and camera. "
                "Note: SwaggerUI cannot be used to test WebSocket connections. "
                "Please use a WebSocket client like Postman or a browser's developer tools. "
                "ユーザーとカメラのためのWebSocket接続。"
                "注意: SwaggerUIではWebSocket接続をテストできません。"
                "Postmanやブラウザの開発者ツールなどのWebSocketクライアントを使用してください。"
            ),
            "tags": ["WebSocket"],
            "parameters": [
                {
                    "name": "user_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                },
                {
                    "name": "camera_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                },
            ],
            "responses": {
                "101": {"description": "Switching Protocols"},
                "400": {"description": "Bad Request"},
                "404": {"description": "Not Found"},
            },
        }
    }
    # タグの順序を指定
    openapi_schema["tags"] = [
        {
            "name": "WebSocket",
            "description": "Operations related to WebSocket connections",
        },
        # 他のタグをここに追加
    ] + openapi_schema.get("tags", [])

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI(lifespan=lifespan)
app.openapi = custom_openapi


try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Mounted static directory")
except Exception as e:
    logger.error(f"Error mounting static directory: {e}")


app.include_router(usercamera.router_v1, prefix="/v1")
app.include_router(usercamera_instance.router_v1, prefix="/v1")
app.include_router(wss.router_v1, prefix="/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to the Japan Tourism Info API"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=env_info.CLOUD_PORT,
        log_level="info",
        reload=True,
    )

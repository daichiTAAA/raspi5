# {
#   "camera_id": "cam1",
#   "rtsp_url": "rtsp://192.168.0.101:8554/stream1"
# }


from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles

# from fastapi.middleware.cors import CORSMiddleware

from api.routers import camera
from api.setup_logger import setup_logger

logger, log_decorator = setup_logger(__name__)


app = FastAPI()
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

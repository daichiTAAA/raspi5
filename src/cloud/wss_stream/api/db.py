from sqlalchemy import create_engine, text

# from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# from pydantic import BaseModel

from api.get_env import get_env_info


# class EnvInfo(BaseModel):
#     PG_VERSION: str = "16.2"
#     PG_CONTAINER_NAME: str = "pgsql_db"
#     PG_HOST: str = "pgsql-db"
#     PG_USER: str = "postgres"
#     PG_PASSWORD: str = "postgres"
#     PG_DATABASE: str = "japan_tourism_info"
#     LOGGER_CONFIG_PATH: str = "logger.ini"


# env_info: EnvInfo = get_env_info(EnvInfo)

# # データベース名を指定せずに接続するためのURLを作成
# SQLALCHEMY_DATABASE_URL_WITHOUT_DB = (
#     f"postgresql+asyncpg://{env_info.PG_USER}:{env_info.PG_PASSWORD}@{env_info.PG_HOST}"
# )
# SQLALCHEMY_DATABASE_URL_WITHOUT_DB_SYNC = (
#     f"postgresql://{env_info.PG_USER}:{env_info.PG_PASSWORD}@{env_info.PG_HOST}"
# )


# # データベース名を指定して接続するためのURLを作成
# SQLALCHEMY_DATABASE_URL = f"{SQLALCHEMY_DATABASE_URL_WITHOUT_DB}/{env_info.PG_DATABASE}"
# SQLALCHEMY_DATABASE_URL_SYNC = (
#     f"{SQLALCHEMY_DATABASE_URL_WITHOUT_DB_SYNC}/{env_info.PG_DATABASE}"
# )

# データベース名を指定せずにエンジンを作成
# db_engine_without_db = create_engine(SQLALCHEMY_DATABASE_URL_WITHOUT_DB)

# # データベースが存在するかどうかをチェックし、存在しなければ作成
# with db_engine_without_db.connect() as conn:
#     try:
#         conn.execute(f"CREATE DATABASE {env_info.PG_DATABASE};")
#         print(f"Database {env_info.PG_DATABASE} created successfully.")
#     except ProgrammingError as e:
#         print(f"Database {env_info.PG_DATABASE} already exists.")
#     except Exception as e:
#         print(f"An error occurred: {e}")

# データベース名を指定してエンジンを作成
# db_engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
# db_engine_sync = create_engine(SQLALCHEMY_DATABASE_URL_SYNC)

# SessionLocal = sessionmaker(
#     autocommit=False, autoflush=False, bind=db_engine, class_=AsyncSession
# )

Base = declarative_base()

ASYNC_DB_URL = "sqlite+aiosqlite:///./data.db"
async_engine = create_async_engine(ASYNC_DB_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession
)


async def get_db():
    async with SessionLocal() as session:
        yield session

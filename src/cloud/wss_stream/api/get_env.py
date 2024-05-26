import os
from pydantic import ValidationError, TypeAdapter
from typing import Type, TypeVar

from dotenv import load_dotenv


T = TypeVar("T")
S = TypeVar("S")


def create_instance_from_env(dataclass_type: Type[T]) -> T:
    load_dotenv()
    field_info = dataclass_type.__annotations__

    init_values = {}
    for field_name, field_type in field_info.items():
        env_value = os.getenv(field_name.upper())  # 環境変数は大文字で取得
        if env_value is not None:
            try:
                # TypeAdapterを使用して型変換を試みる
                adapter = TypeAdapter(field_type)
                converted_value = adapter.validate_python(env_value)
            except ValidationError:
                # バリデーションエラーが発生した場合は、変換せずに元の値を使用
                converted_value = env_value
            init_values[field_name] = converted_value

    try:
        return dataclass_type(**init_values)
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise


def get_env_info(env_info_class: Type[S]) -> S:
    """環境変数から設定を読み込んで、指定されたデータクラスのインスタンスを作成する

    Arguments:
    ----------
        env_info_class (Type[BaseModel]): 環境変数から読み込む設定のデータクラス

    Notes:
    ------
    使用例:
    ```python
    class EnvInfo(BaseModel):
        PG_VERSION: str
        PG_CONTAINER_NAME: str
        PG_HOST: str
        PG_USER: str
        PG_PASSWORD: str
        REDIS_PASSWORD: str

    env_info: EnvInfo = get_env_info(EnvInfo)
    PG_USER = env_info.PG_USER
    ```
    """
    # .envファイルを探して、あれば読み込む
    load_dotenv()
    env_info_instance = create_instance_from_env(env_info_class)
    return env_info_instance

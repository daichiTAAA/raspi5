from typing import Dict, Tuple
from pydantic import BaseModel

from api.models.usercamera_instance import UserCameraInstance


class UserCameraInstances(BaseModel):
    """
    使用例
    ```
    UserCameraInstances.add_instance("user1", "camera1", UserInstance(...))
    instance = UserCameraInstances.get_instance("user1", "camera1")
    ```
    """

    user_id: str
    camera_id: str
    usercamera_instance: UserCameraInstance

    _instances: Dict[Tuple[str, str], UserCameraInstance] = {}

    @classmethod
    def add_instance(
        cls, user_id: str, camera_id: str, usercamera_instance: UserCameraInstance
    ):
        cls._instances[(user_id, camera_id)] = usercamera_instance

    @classmethod
    def get_instance(cls, user_id: str, camera_id: str) -> UserCameraInstance:
        return cls._instances.get((user_id, camera_id))

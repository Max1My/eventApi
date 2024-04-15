from enum import Enum

from pydantic import BaseModel

from src.common.base_dto import PydanticBaseModel


class RoleView(PydanticBaseModel):
    name: str


class CreateRole(BaseModel):
    name: str


class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

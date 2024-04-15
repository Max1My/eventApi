from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy_utils import Password

from src.common.base_dto import PydanticBaseModel
from src.core.domain.roles.dto import RoleView


class AuthUser(BaseModel):
    username: str
    password: str


class UpdateUser(BaseModel):
    first_name: str
    username: str
    password: str | None = None


class UpdatePasswordUser(BaseModel):
    password: str


class ReturnedUser(PydanticBaseModel):
    id: int
    first_name: str
    username: str


class UnprotectedUserView(ReturnedUser):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    password: Password


class CreatedUserId(BaseModel):
    id: int


class CreateUser(BaseModel):
    first_name: str
    username: str
    password: str
    role_id: int


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    username: str | None = None

    def __init__(self, username: str, **data: Any):
        super().__init__(**data)
        self.username = username


class UserView(ReturnedUser):
    role: RoleView | None = Field(exclude=True, example="")
    ...

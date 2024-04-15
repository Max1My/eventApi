from pydantic import BaseModel


class AuthUser(BaseModel):
    username: str
    password: str


class UpdateUser(BaseModel):
    first_name: str
    username: str


class RegisterUser(BaseModel):
    first_name: str
    username: str
    password: str


class ResetPasswordRequest(BaseModel):
    password: str

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError

from src.core.domain.roles.service import RoleService
from src.core.domain.users import requests, dto
from src.core.domain.users.dto import (
    AuthUser,
    TokenData
)
from src.core.domain.users.repository import UserRepository
from src.settings import SECRET_KEY, ALGORITHM, oauth2_scheme


class UserService:

    def __init__(
            self
    ) -> None:
        self.repository = UserRepository()
        self.role_service = RoleService()

    async def authenticate(
            self,
            user_data: AuthUser
    ) -> AuthUser:
        return await self.repository.read_encoded(user_data)

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    async def get_by_username(self, username: str) -> dto.UserView:
        return await self.repository.get_user_by_username(username)

    async def get_user(self, token: str = Depends(oauth2_scheme)) -> dto.UserView:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные авторизационные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = await self.get_by_username(token_data.username)
        if user is None:
            raise credentials_exception
        return user

    async def register(self, request: requests.RegisterUser, role_name: str) -> dto.UnprotectedUserView:
        role = await self.role_service.get_or_create_role_by_name(role_name)
        request_data = request.model_dump()
        request_data['role_id'] = role.id
        user_data = dto.CreateUser.model_validate(request_data)
        return await self.repository.create(user_data)

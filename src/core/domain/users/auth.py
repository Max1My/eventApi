from typing import List, Union

from fastapi import Depends, HTTPException
from starlette import status
from starlette.requests import Request

from src.core.domain.users.service import oauth2_scheme, UserService
from . import dto
from ..roles.dto import RoleEnum


class Auth:
    def __init__(
            self,
            roles: Union[List[Union[RoleEnum, str]], RoleEnum, str, None] = None
    ):
        if not isinstance(roles, list) and roles is not None:
            self.roles = [roles]
        else:
            self.roles = roles

    async def __call__(
            self,
            request: Request,
            token: str = Depends(oauth2_scheme),
            service: UserService = Depends(),
    ) -> dto.UserView:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные авторизационные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
        user = await service.get_user(token)
        if user is None or not self.check_user(user):
            raise credentials_exception from None
        return user

    def check_user(self, user: dto.UserView) -> bool:
        if user.role in self.roles or user.role.name in self.roles:
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
            headers={"WWW-Authenticate": "Bearer"}
        )

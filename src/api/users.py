from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from src.common.fastapi_jwt_auth import AuthJWT
from src.core.domain.roles.dto import RoleEnum
from src.core.domain.users import errors, requests, dto
from src.core.domain.users.auth import Auth
from src.core.domain.users.dto import UserView
from src.core.domain.users.service import UserService
from src.settings import ACCESS_TOKEN_EXPIRE_DAYS

from src.core.domain.events.event_members import errors as event_member_errors
from src.core.domain.events.event_members import response as event_member_response
from src.core.domain.events.event_members.service import EventMemberService

user_router = APIRouter()
service = UserService()
event_member_service = EventMemberService()


@user_router.post(
    path='/signin',
    status_code=status.HTTP_200_OK,
    tags=['Пользователь'],
    name='Авторизация пользователя',
)
async def signin(
        request: requests.AuthUser,
        Authorize: AuthJWT = Depends()
) -> dto.Token:
    if request.username and request.password:
        user_in_db = await service.authenticate(dto.AuthUser(
            username=request.username,
            password=request.password
        ))
        if not user_in_db:
            raise errors.UsersHTTPError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Не удалось войти в личный кабинет',
                headers={'WWW-Authenticate': 'Bearer'},
            )
        access_token_expires = timedelta(days=int(ACCESS_TOKEN_EXPIRE_DAYS))
        access_token = Authorize.create_access_token(subject=user_in_db.username, expires_time=access_token_expires)
        refresh_token = Authorize.create_refresh_token(subject=user_in_db.username, expires_time=access_token_expires)
        return dto.Token(access_token=access_token, refresh_token=refresh_token)
    else:
        raise errors.UsersHTTPError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Обязательные поля должны быть заполнены: email, пароль'
        )


@user_router.post(
    path='/refresh',
    status_code=status.HTTP_200_OK,
    tags=['Пользователь'],
    name='Обновить токен',
)
async def refresh(
        Authorize: AuthJWT = Depends()
):
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    return {"access_token": new_access_token}


@user_router.post(
    path='/register',
    status_code=status.HTTP_201_CREATED,
    tags=['Пользователь'],
    name='Регистрация пользователя'
)
async def register_user(
        request: requests.RegisterUser,
        Authorize: AuthJWT = Depends()
):
    user = await service.register(request, RoleEnum.USER.name)
    if not user:
        raise errors.UsersHTTPError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не удалось зарегистрироваться',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(days=int(ACCESS_TOKEN_EXPIRE_DAYS))
    access_token = Authorize.create_access_token(subject=user.username, expires_time=access_token_expires)
    refresh_token = Authorize.create_refresh_token(subject=user.username, expires_time=access_token_expires)
    return dto.Token(access_token=access_token, refresh_token=refresh_token)


@user_router.post(
    path='/register/admin',
    status_code=status.HTTP_201_CREATED,
    tags=['Пользователь'],
    name='Регистрация администратора'
)
async def register_user(
        request: requests.RegisterUser,
        _: Annotated[UserView, Depends(Auth([RoleEnum.ADMIN]))],
        Authorize: AuthJWT = Depends()
):
    user = await service.register(request, RoleEnum.ADMIN.name)
    if not user:
        raise errors.UsersHTTPError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не удалось зарегистрироваться',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(days=int(ACCESS_TOKEN_EXPIRE_DAYS))
    access_token = Authorize.create_access_token(subject=user.username, expires_time=access_token_expires)
    refresh_token = Authorize.create_refresh_token(subject=user.username, expires_time=access_token_expires)
    return dto.Token(access_token=access_token, refresh_token=refresh_token)


@user_router.get(
    path='/event',
    status_code=status.HTTP_200_OK,
    tags=['Пользователь'],
    name='Получить мероприятия пользователя'
)
async def get_events_user(
        user: Annotated[UserView, Depends(Auth([RoleEnum.ADMIN, RoleEnum.USER]))]
):
    events = await event_member_service.get_all(user_id=user.id)
    if events is None:
        raise event_member_errors.EventMemberHTTPError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Не удалось прочитать всех мероприятий'
        )
    return [event_member_response.EventMemberResponse(
        event_id=event.event_id,
        name=event.event.name
    ) for event in events]


@user_router.post(
    path='/event/{event_id}',
    status_code=status.HTTP_201_CREATED,
    tags=['Пользователь'],
    name='Записаться на мероприятие'
)
async def create_event_member(
        event_id: int,
        user: Annotated[UserView, Depends(Auth([RoleEnum.ADMIN, RoleEnum.USER]))]
):
    event_member = await event_member_service.create(event_id=event_id, user_id=user.id)
    if not event_member:
        raise event_member_errors.EventMemberHTTPError(
            status_code=status.HTTP_409_CONFLICT,
            detail='Не удалось записаться на мероприятие'
        )


@user_router.delete(
    path='/event/{event_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['Пользователь'],
    name='Отменить запись на мероприятие'
)
async def delete_event_member(
        event_id: int,
        user: Annotated[UserView, Depends(Auth([RoleEnum.ADMIN, RoleEnum.USER]))]
):
    deleted_event_member = await event_member_service.delete(event_id=event_id, user_id=user.id)
    if not deleted_event_member:
        raise event_member_errors.EventMemberHTTPError(
            status_code=status.HTTP_409_CONFLICT,
            detail='Не удалось отменить записать на мероприятие'
        )
    return True

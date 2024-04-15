from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from src.core.domain.events import requests
from src.core.domain.events.event_members.response import EventMemberListResponse
from src.core.domain.events.event_members.service import EventMemberService
from src.core.domain.events.service import EventService
from src.core.domain.events import errors
from src.core.domain.roles.dto import RoleEnum
from src.core.domain.users.auth import Auth
from src.core.domain.users.dto import UserView
from src.core.domain.events import response

event_router = APIRouter()
service = EventService()
event_member_service = EventMemberService()


@event_router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    tags=['Мероприятия'],
    name='Получить все мероприятия',
)
async def get_all_events() -> list[response.EventResponse]:
    events = await service.get_all()
    if events is None:
        return []
    return [
        response.EventResponse(
            id=event.id,
            name=event.name,
            started_at=event.started_at,
            finished_at=event.finished_at,
            members=[EventMemberListResponse(
                name=member.user.first_name
            ) for member in await event_member_service.get_members_by_event_id(event_id=event.id)]
        ) for event in events
    ]


@event_router.get(
    path='/{id}',
    status_code=status.HTTP_200_OK,
    tags=['Мероприятия'],
    name='Получить мероприятие'
)
async def get_event(
        id: int,
) -> response.EventResponse:
    event_model = await service.get(event_id=id)
    if event_model is None:
        raise errors.EventHTTPError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Мероприятие не найдено'
        )
    return response.EventResponse(
        id=event_model.id,
        name=event_model.name,
        started_at=event_model.started_at,
        finished_at=event_model.finished_at,
        members=[EventMemberListResponse(
            name=member.user.first_name
        ) for member in await event_member_service.get_members_by_event_id(event_id=event_model.id)]
    )


@event_router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    tags=['Мероприятия'],
    name='Создать мероприятие',
)
async def create_event(
        request: requests.CreateEvent,
        _: Annotated[UserView, Depends(Auth([RoleEnum.ADMIN]))]
):
    event_model = await service.create(request=request)
    if not event_model:
        raise errors.EventHTTPError(
            status_code=status.HTTP_409_CONFLICT,
            detail='Не удалось создать мероприятие'
        )


@event_router.delete(
    path='/{id}',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['Мероприятия'],
    name='Удалить мероприятие'
)
async def delete_event(
        id: int,
        _: Annotated[UserView, Depends(Auth([RoleEnum.ADMIN]))]
):
    deleted_event = await service.delete(event_id=id)
    if not deleted_event:
        raise errors.EventHTTPError(
            status_code=status.HTTP_409_CONFLICT,
            detail='Не удалось удалить мероприятие'
        )
    return True

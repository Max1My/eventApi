from src.core.domain.events.event_members import requests, dto
from src.core.domain.events.event_members.repository import EventMemberRepository


class EventMemberService:
    def __init__(
            self
    ) -> None:
        self._repository = EventMemberRepository()

    async def create(self, event_id: int, user_id: int) -> dto.EventView:
        request_data = {
            "event_id": event_id,
            "user_id": user_id
        }
        create_data = dto.EventMemberCreate.model_validate(request_data)
        return await self._repository.create(create_data)

    async def get_all(
            self,
            user_id: int
    ) -> list[dto.EventMemberView]:
        return await self._repository.get_all(user_id=user_id)

    async def get(self, event_id: int, user_id: int) -> dto.EventMemberView:
        return await self._repository.get_by_event_id(event_id=event_id, user_id=user_id)

    async def get_members_by_event_id(self, event_id: int) -> list[dto.EventMemberView]:
        return await self._repository.get_events_by_event_id(event_id=event_id)

    async def delete(self, event_id: int, user_id: int):
        return await self._repository.delete(event_id=event_id, user_id=user_id)

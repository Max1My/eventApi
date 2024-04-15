from src.core.domain.events import requests, dto
from src.core.domain.events.event_members.repository import EventMemberRepository
from src.core.domain.events.repository import EventRepository


class EventService:
    def __init__(
            self
    ) -> None:
        self._repository = EventRepository()
        self.event_member_repository = EventMemberRepository()

    async def create(self, request: requests.CreateEvent) -> dto.EventView:
        create_data = dto.EventCreate.model_validate(request.model_dump())
        return await self._repository.create(create_data)

    async def get_all(
            self
    ) -> list[dto.EventView]:
        return await self._repository.get_all()

    async def get(self, event_id: int) -> dto.EventView:
        return await self._repository.get_by_id(event_id=event_id)

    async def delete(self, event_id: int):
        await self.event_member_repository.delete_by_event_id(event_id=event_id)
        return await self._repository.delete(event_id=event_id)

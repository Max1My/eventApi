from datetime import datetime

from src.common.base_dto import PydanticBaseModel
from src.core.domain.events.event_members.response import EventMemberListResponse


class EventResponse(PydanticBaseModel):
    name: str
    started_at: datetime
    finished_at: datetime
    members: list[EventMemberListResponse] | None = None

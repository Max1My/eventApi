from datetime import datetime

from pydantic import BaseModel, Field

from src.common.base_dto import PydanticBaseModel
from src.core.domain.events.dto import EventView
from src.core.domain.users.dto import UserView


class EventMember(PydanticBaseModel):
    user_id: int
    event_id: int


class EventMemberView(EventMember):
    user: UserView | None = Field(exclude=True, example="")
    event: EventView | None = Field(exclude=True, example="")


class EventMemberCreate(BaseModel):
    user_id: int
    event_id: int

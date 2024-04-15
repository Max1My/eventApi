from datetime import datetime

from pydantic import BaseModel

from src.common.base_dto import PydanticBaseModel


class Event(PydanticBaseModel):
    name: str
    started_at: datetime
    finished_at: datetime


class EventView(Event):
    ...


class EventCreate(BaseModel):
    name: str
    started_at: datetime
    finished_at: datetime

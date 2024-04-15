from datetime import datetime

from pydantic import BaseModel


class CreateEventMember(BaseModel):
    event_id: int

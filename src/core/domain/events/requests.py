from datetime import datetime

from pydantic import BaseModel


class CreateEvent(BaseModel):
    name: str
    started_at: datetime
    finished_at: datetime

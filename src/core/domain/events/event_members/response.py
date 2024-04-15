from pydantic import BaseModel


class EventMemberResponse(BaseModel):
    event_id: int
    name: str


class EventMemberListResponse(BaseModel):
    name: str

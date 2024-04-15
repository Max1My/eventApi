from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    first_name: str
    email: str
    role: str

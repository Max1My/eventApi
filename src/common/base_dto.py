from pydantic import BaseModel


class PydanticBaseModel(BaseModel):
    id: int | None = None

    class Config:
        orm_mode = True

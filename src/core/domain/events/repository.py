from loguru import logger
from sqlalchemy import select, delete
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import joinedload

from src.common.base import BaseRepository
from src.core.domain.events import dto
from src.core.domain.events.models import Event


class EventRepository(BaseRepository):
    database_model = Event
    view_model = dto.EventView

    def __init__(self):
        super().__init__()
        self.base_stmt = self.__base_stmt()

    def __base_stmt(self):
        stmt = (
            select(self.database_model)
        )
        return stmt

    async def create(self, data: dto.EventCreate):
        async with self.session() as session:
            async with session.begin():
                model = self._pydantic_to_model(data, self.database_model())
                session.add(model)
                await session.commit()
            await session.refresh(model)
            return model

    async def get_all(self) -> list[dto.EventView]:
        async with self.session() as session:
            async with session.begin():
                stmt = (
                    self.base_stmt
                )
                items = (await session.scalars(stmt)).unique().all()
                if items:
                    return [self._model_to_pydantic(item, self.view_model) for item in items]

    async def get_by_id(self, event_id: int) -> dto.EventView:
        async with self.session() as session:
            async with session.begin():
                stmt = (
                    self.base_stmt
                    .where(self.database_model.id == event_id)
                )
                item = (await session.scalars(stmt)).unique().first()
                if item:
                    return self._model_to_pydantic(item, self.view_model)

    async def delete(self, event_id: int) -> bool:
        async with self.session() as session:
            async with session.begin():
                try:
                    stmt = (
                        delete(self.database_model)
                        .where(self.database_model.id == event_id)
                        .returning(self.database_model)
                    )
                    await session.scalars(stmt)
                    await session.commit()
                    logger.info('Мероприятие удалено')
                    return True
                except DatabaseError as e:
                    await session.rollback()
                    logger.info(f'Ошибка при удалении мероприятия: {e}')
                    return False

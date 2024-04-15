from loguru import logger
from sqlalchemy import select, delete
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import joinedload

from src.common.base import BaseRepository
from src.core.domain.events.event_members import dto
from src.core.domain.events.event_members.models import EventMembers


class EventMemberRepository(BaseRepository):
    database_model = EventMembers
    view_model = dto.EventMemberView

    def __init__(self):
        super().__init__()
        self.base_stmt = self.__base_stmt()

    def __base_stmt(self):
        stmt = (
            select(self.database_model)
            .options(
                joinedload(self.database_model.user),
                joinedload(self.database_model.event)
            )
        )
        return stmt

    async def create(self, data: dto.EventMemberCreate):
        async with self.session() as session:
            async with session.begin():
                model = self._pydantic_to_model(data, self.database_model())
                session.add(model)
                await session.commit()
            await session.refresh(model)
            return model

    async def get_all(self, user_id: int) -> list[dto.EventMemberView]:
        async with self.session() as session:
            async with session.begin():
                stmt = (
                    self.base_stmt
                    .where(self.database_model.user_id == user_id)
                )
                items = (await session.scalars(stmt)).unique().all()
                if items:
                    return [self._model_to_pydantic(item, self.view_model) for item in items]

    async def get_by_event_id(self, event_id: int, user_id: int) -> dto.EventMemberView:
        async with self.session() as session:
            async with session.begin():
                stmt = (
                    self.base_stmt
                    .where(self.database_model.event_id == event_id)
                    .where(self.database_model.user_id == user_id)
                )
                item = (await session.scalars(stmt)).unique().first()
                if item:
                    return self._model_to_pydantic(item, self.view_model)

    async def get_events_by_event_id(self, event_id: int) -> list[dto.EventMemberView]:
        async with self.session() as session:
            async with session.begin():
                stmt = (
                    self.base_stmt
                    .where(self.database_model.event_id == event_id)
                )
                items = (await session.scalars(stmt)).unique().all()
                if items:
                    return [self._model_to_pydantic(item, self.view_model) for item in items]
                return []

    async def delete(self, event_id: int, user_id: int) -> bool:
        async with self.session() as session:
            async with session.begin():
                try:
                    stmt = (
                        delete(self.database_model)
                        .where(self.database_model.event_id == event_id)
                        .where(self.database_model.user_id == user_id)
                        .returning(self.database_model)
                    )
                    await session.scalars(stmt)
                    await session.commit()
                    logger.info('Запись на Мероприятие удалено')
                    return True
                except DatabaseError as e:
                    await session.rollback()
                    logger.info(f'Ошибка при удалении Записи на мероприятие: {e}')
                    return False

    async def delete_by_event_id(self, event_id: int) -> bool:
        async with self.session() as session:
            async with session.begin():
                try:
                    stmt = (
                        delete(self.database_model)
                        .where(self.database_model.event_id == event_id)
                        .returning(self.database_model)
                    )
                    await session.scalars(stmt)
                    await session.commit()
                    logger.info('Запись на Мероприятие удалено')
                    return True
                except DatabaseError as e:
                    await session.rollback()
                    logger.info(f'Ошибка при удалении Записи на мероприятие: {e}')
                    return False

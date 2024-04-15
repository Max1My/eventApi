from collections.abc import Sequence

from loguru import logger
from sqlalchemy import select, update, delete
from sqlalchemy.exc import DatabaseError

from src.common.base import BaseRepository
from src.core.domain.roles import dto
from src.core.domain.roles import models


class RoleRepository(BaseRepository):
    database_model = models.Role
    view_model = dto.RoleView

    def __init__(self):
        super().__init__()
        self.base_stmt = self.__base_stmt()

    def __base_stmt(self):
        stmt = (
            select(self.database_model)
        )
        return stmt

    async def create(self, data: dto.CreateRole):
        async with self.session() as session:
            async with session.begin():
                model = self._pydantic_to_model(data, self.database_model())
                session.add(model)
                await session.commit()
            await session.refresh(model)
            return model

    async def read(self, role_id: int) -> Sequence[models.Role] | bool:
        stmt = (
            select(self.database_model).where(
                self.database_model.id == role_id
            )
        )
        async with self.session() as session:
            try:
                result = (await session.scalars(stmt)).first()
                logger.info('Роль прочитана')
                return self._model_to_pydantic(result, self.view_model)
            except DatabaseError as e:
                await session.rollback()
                logger.info(f'Ошибка при чтении роли: {e}')
                return False

    async def read_by_name(self, name: str):
        async with self.session() as session:
            async with session.begin():
                stmt = (
                    self.base_stmt
                    .where(self.database_model.name == name)
                )
                item = (await session.scalars(stmt)).unique().first()
                if item:
                    return self._model_to_pydantic(item, self.view_model)

    async def read_all(self) -> list:
        stmt = (
            select(models.Role)
        )
        async with self.session() as session:
            try:
                result = (await session.scalars(stmt)).all()
                logger.info('Все роли прочитаны')
                return [self._model_to_pydantic(sa_model, dto.RoleView) for sa_model in result]
            except DatabaseError as e:
                await session.rollback()
                logger.info(f'Ошибка при чтении всех ролей: {e}')
                return []

    async def delete(self, role_id: int) -> bool:
        stmt = (
            delete(models.Role)
            .where(models.Role.id == role_id)
            .returning(models.Role)
        )
        async with self.session() as session:
            try:
                await session.scalars(stmt)
                await session.commit()
                logger.info('Роль удалена')
                return True
            except DatabaseError as e:
                await session.rollback()
                logger.info(f'Ошибка при удалении роли: {e}')
                return False

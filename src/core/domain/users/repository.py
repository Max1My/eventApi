from loguru import logger
from passlib.hash import pbkdf2_sha512
from sqlalchemy import select, delete
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import joinedload

from src.common.base import BaseRepository
from src.core.domain.users import dto
from src.core.domain.users import models


class UserRepository(BaseRepository):
    database_model = models.User
    view_model = dto.ReturnedUser

    def __init__(self):
        super().__init__()
        self.base_stmt = self.__base_stmt()

    def __base_stmt(self):
        stmt = (
            select(self.database_model)
            .options(joinedload(self.database_model.role))
        )
        return stmt

    async def create(self, data: dto.CreateUser) -> dto.UnprotectedUserView:
        async with self.session() as session:
            async with session.begin():
                model = self._pydantic_to_model(data, self.database_model())
                session.add(model)
                await session.commit()
            await session.refresh(model)
            return self._model_to_pydantic(model, dto.UnprotectedUserView)

    async def read_encoded(self, user_data: dto.AuthUser) -> dto.AuthUser | bool:
        passHash = pbkdf2_sha512.encrypt(user_data.password)
        stmt = (
            select(self.database_model)
            .where(self.database_model.username == user_data.username)
        )

        async with self.session() as session:
            model = (await session.scalars(stmt)).unique().first()
            print(f'model: {model}')
            if model:
                user = self._model_to_pydantic(model, dto.UnprotectedUserView)
                if pbkdf2_sha512.verify(user_data.password, passHash):
                    return dto.AuthUser(
                        first_name=user.first_name,
                        username=user.username,
                        password=passHash,
                    )

        return False

    async def read(self, user_id: int) -> dto.UserView:
        async with self.session() as session:
            async with session.begin():
                stmt = (
                    self.base_stmt
                    .where(self.database_model.id == user_id)
                )
                item = (await session.scalars(stmt)).unique().first()
                if item:
                    return self._model_to_pydantic(item, dto.UserView)

    async def read_unprotected(self, user_id: int) -> dto.UnprotectedUserView:
        async with self.session() as session:
            async with session.begin():
                stmt = (
                    self.base_stmt
                    .where(self.database_model.id == user_id)
                )
                model = (await session.scalars(stmt)).unique().first()
                if model:
                    return self._model_to_pydantic(model, dto.UnprotectedUserView)

    async def update(self, update_data: dto.UpdateUser,
                     model: dto.ReturnedUser):
        async with self.session() as session:
            async with session.begin():
                model = self._pydantic_to_model(model, self.database_model())
                update_model = self._pydantic_to_model(update_data, model)
                updated_item = await session.merge(update_model)
            await session.commit()
            return updated_item

    async def delete(self, user_id: int) -> bool:
        stmt = (
            delete(models.User)
            .where(models.User.id == user_id)
            .returning(models.User)
        )
        async with self.session() as session:
            try:
                await session.scalars(stmt)
                await session.commit()
                logger.info('Пользователь удален')
                return True
            except DatabaseError as e:
                await session.rollback()
                logger.info(f'Ошибка при удалении пользователя: {e}')
                return False

    async def get_user_by_username(self, username: str) -> dto.UserView:
        async with self.session() as session:
            stmt = (
                self.base_stmt
                .where(self.database_model.username == username)
            )
            model = (await session.scalars(stmt)).unique().first()
            if model:
                return self._model_to_pydantic(model, dto.UserView)

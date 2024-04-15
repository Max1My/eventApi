from src.core.domain.roles import requests, dto
from src.core.domain.roles.dto import RoleView
from src.core.domain.roles.repository import RoleRepository


class RoleService:
    def __init__(
            self
    ) -> None:
        self.repository = RoleRepository()

    async def create(
            self,
            request: requests.CreateRole
    ) -> RoleView:
        data = dto.CreateRole(name=request.name)
        return await self.repository.create(data)

    async def read(
            self,
            role_id: int
    ) -> RoleView:
        return await self.repository.read(role_id)

    async def get_by_name(self, name: str):
        return await self.repository.read_by_name(name)

    async def read_all(
            self
    ) -> list:
        return await self.repository.read_all()

    async def delete(
            self,
            role_id: int
    ) -> bool:
        return await self.repository.delete(role_id)

    async def get_or_create_role_by_name(self, name: str) -> RoleView:
        name = dto.RoleEnum[name].value
        role = await self.get_by_name(name=name)
        if not role:
            data = dto.CreateRole(name=name)
            return await self.repository.create(data)
        return role

    async def get_or_create_user_role(self) -> RoleView:
        role = await self.get_by_name(name=dto.RoleEnum.USER.value)
        if not role:
            data = dto.CreateRole(name=dto.RoleEnum.USER.value)
            return await self.repository.create(data)
        return role

    async def get_or_create_admin_role(self) -> RoleView:
        role = await self.get_by_name(name=dto.RoleEnum.ADMIN.value)
        if not role:
            data = dto.CreateRole(name=dto.RoleEnum.ADMIN.value)
            return await self.repository.create(data)
        return role

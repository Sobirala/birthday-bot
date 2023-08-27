from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Base
from bot.repositories.congratulation import CongratulationRepository
from bot.repositories.group import GroupRepository
from bot.repositories.user import UserRepository


class UnitOfWork:
    _session: AsyncSession

    users: UserRepository
    groups: GroupRepository
    congratulations: CongratulationRepository

    def __init__(self, session: AsyncSession):
        self._session = session

    async def __aenter__(self) -> Self:
        self.users = UserRepository(self._session)
        self.groups = GroupRepository(self._session)
        self.congratulations = CongratulationRepository(self._session)

        return self

    async def __aexit__(self, *args):
        ...

    async def commit(self):
        await self._session.commit()

    async def delete(self, model: Base):
        await self.delete(model)

    async def rollback(self):
        await self._session.rollback()

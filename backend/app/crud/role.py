from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.role import Role


class CRUDRole(CRUDBase):

    async def get_by_name(
        self,
        name: str,
        session: AsyncSession
    ) -> Role:
        post_db = await session.execute(
            select(Role).where(
                Role.name == name
            )
        )
        return post_db.scalars().first()

role_crud = CRUDRole(Role)
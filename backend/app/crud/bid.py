from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.bid import Bid


class CRUDBid(CRUDBase):
    async def create(
        self,
        obj_in,
        executor_id,
        session: AsyncSession,
    ):
        obj_in_data = obj_in.dict()
        obj_in_data["executor_id"] = executor_id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_by_executor_id_and_task_id(
        self, task_id, executor_id, session: AsyncSession
    ):
        obj = await session.execute(
            select(Bid).where(Bid.executor_id == executor_id, Bid.task_id == task_id)
        )
        return obj.scalars().first()


bid_crud = CRUDBid(Bid)

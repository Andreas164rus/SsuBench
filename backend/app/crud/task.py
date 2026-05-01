from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.task import Task


class CRUDTask(CRUDBase):
    async def create(
        self,
        obj_in,
        customer_id,
        session: AsyncSession,
    ):
        obj_in_data = obj_in.dict()
        obj_in_data["customer_id"] = customer_id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj


task_crud = CRUDTask(Task)

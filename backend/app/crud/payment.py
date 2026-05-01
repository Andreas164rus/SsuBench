from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models.payment import Payment


class CRUDPayment(CRUDBase):
    async def create(
        self,
        user_id: int,
        task_id: int,
        value: float,
        session: AsyncSession,
    ):

        db_obj = self.model(**{"user_id": user_id, "task_id": task_id, "value": value})
        session.add(db_obj)


payment_crud = CRUDPayment(Payment)

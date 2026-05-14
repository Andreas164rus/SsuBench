from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.payment import Payment
from typing import Optional


class CRUDPayment(CRUDBase):
    async def create(
        self,
        from_user: int,
        to_user: int,
        task_id: Optional[int],
        value: float,
        session: AsyncSession,
    ):

        db_obj = self.model(
            **{
                "from_user": from_user,
                "to_user": to_user,
                "task_id": task_id,
                "value": value,
            }
        )
        session.add(db_obj)
        return db_obj


payment_crud = CRUDPayment(Payment)

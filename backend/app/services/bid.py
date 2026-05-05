from app.models.bid import Bid
from app.models.task import Task
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.crud.task import task_crud


class BidService:
    def __init__(self, session):
        self.session = session

    async def get_bids_by_task(self, task_id, customer_id):
        task: Task = await task_crud.get(task_id, self.session)
        if task.customer_id != customer_id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Ты не можешь смотреть откликина чужую задачу",
            )
        return (
            select(Bid).where(Bid.task_id == task_id).options(joinedload(Bid.executor))
        )

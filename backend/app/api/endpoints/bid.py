from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.user import (
    customer_user,
    executor_user,
)
from app.core.db import get_async_session
from app.schemas.bid import BidDB, BidWithExecutor
from app.models.user import User
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from app.services.bid import BidService
from app.services.task import TaskService


router = APIRouter(prefix="/bid")


@router.get(
    "/who_responsed_by_task/{task_id}",
    response_model=Page[BidWithExecutor],
    tags=["bid"],
)
async def who_responsed_by_task(
    task_id: int,
    user: User = Depends(customer_user),
    session: AsyncSession = Depends(get_async_session),
):
    bid_service = BidService(session)
    query = await bid_service.get_bids_by_task(task_id, user.id)
    return await paginate(session, query)


@router.post("/{task_id}/response/", response_model=BidDB, tags=["bid"])
async def response_to_a_task(
    task_id: int,
    user: User = Depends(executor_user),
    session: AsyncSession = Depends(get_async_session),
):
    task_service = TaskService(session)
    task = await task_service.response_task(task_id, user.id)
    return task

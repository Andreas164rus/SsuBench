from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.user import (
    auth_backend,
    fastapi_users,
    current_superuser,
    current_user,
    customer_user,
    executor_user,
)
from sqlalchemy.orm import selectinload, joinedload
from app.core.db import get_async_session
from app.schemas.bid import BidDB, CreateBid, BidWithExecutor
from app.models.user import User
from app.crud.bid import bid_crud
from app.models.task import Task
from app.crud.task import task_crud
from sqlalchemy import select, not_, exists
from app.models.bid import Bid
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from app.services.bid import BidService


router = APIRouter(prefix="/bid")


@router.post("/response/", response_model=BidDB, tags=["bid"])
async def response_to_a_task(
    data: CreateBid,
    user: User = Depends(executor_user),
    session: AsyncSession = Depends(get_async_session),
):
    task = await task_crud.get(data.task_id, session)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такой задачи не существует!",
        )
    selected_task = await bid_crud.get_by_executor_id_and_task_id(
        data.task_id, user.id, session
    )
    if selected_task is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы уже откликнулись на задачу!",
        )
    bid = await bid_crud.create(data, user.id, session)
    return bid


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


# @router.get("/open/", response_model=Page[TaskDB], tags=["bid"])
# async def get_not_busy_tasks(
#     user: User = Depends(current_user),
#     session: AsyncSession = Depends(get_async_session),
# ):
#     return await paginate(
#         session,
#         select(Task)
#         .where(not_(exists().where(Bid.task_id == Task.id)))
#         .order_by(Task.created),
#     )


# @router.get("/all/", response_model=Page[TaskDB], tags=["bid"])
# async def all(
#     user: User = Depends(current_user),
#     session: AsyncSession = Depends(get_async_session),
# ):
#     return await paginate(session, select(Task).order_by(Task.created))


# @router.get("/my_tasks/", response_model=Page[TaskDB], tags=["bid"])
# async def my(
#     user: User = Depends(customer_user),
#     session: AsyncSession = Depends(get_async_session),
# ):
#     return await paginate(
#         session, select(Task).where(Task.customer_id == user.id).order_by(Task.created)
#     )

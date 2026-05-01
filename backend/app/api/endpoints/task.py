from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.user import (
    auth_backend,
    fastapi_users,
    current_superuser,
    current_user,
    customer_user,
    executor_user,
)
from app.core.db import get_async_session
from app.schemas.task import CreateTask, TaskDB
from app.models.user import User
from app.crud.task import task_crud
from app.models.task import Task
from sqlalchemy import select, not_, exists
from app.models.bid import Bid
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from app.services.task import TaskService


router = APIRouter(prefix="/task")


@router.post("/{task_id}/user/{executor_id}/", response_model=TaskDB, tags=["task"])
async def select_user_for_a_task(
    task_id: int,
    executor_id: int,
    user: User = Depends(customer_user),
    session: AsyncSession = Depends(get_async_session),
):
    task_service = TaskService(session)
    task = await task_service.select_user_for_task(task_id, user.id, executor_id)
    return task


@router.post("/create/", response_model=TaskDB, tags=["task"])
async def create_task(
    data: CreateTask,
    user: User = Depends(customer_user),
    session: AsyncSession = Depends(get_async_session),
):
    task = await task_crud.create(data, user.id, session)
    return task


@router.get("/open/", response_model=Page[TaskDB], tags=["task"])
async def get_not_busy_tasks(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await paginate(
        session,
        select(Task)
        .where(not_(exists().where(Bid.task_id == Task.id)))
        .order_by(Task.created),
    )


@router.get("/all/", response_model=Page[TaskDB], tags=["task"])
async def all(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await paginate(session, select(Task).order_by(Task.created))


@router.get("/my_tasks/", response_model=Page[TaskDB], tags=["task"])
async def my(
    user: User = Depends(customer_user),
    session: AsyncSession = Depends(get_async_session),
):
    return await paginate(
        session, select(Task).where(Task.customer_id == user.id).order_by(Task.created)
    )


@router.get("/done_task_executor/{task_id}/", response_model=TaskDB, tags=["task"])
async def done_task_by_ex(
    task_id: int,
    user: User = Depends(executor_user),
    session: AsyncSession = Depends(get_async_session),
):
    task_service = TaskService(session)
    task = await task_service.done_task_by_executor(task_id, user.id)
    return task


@router.get("/done_task_customer/{task_id}/", response_model=TaskDB, tags=["task"])
async def done_task_by_cus(
    task_id: int,
    user: User = Depends(customer_user),
    session: AsyncSession = Depends(get_async_session),
):
    task_service = TaskService(session)
    task = await task_service.done_task_by_customer(task_id, user)
    return task


@router.delete("/delete/{task_id}/", response_model=TaskDB, tags=["task"])
async def cancel_task(
    task_id: int,
    user: User = Depends(customer_user),
    session: AsyncSession = Depends(get_async_session),
):
    task_service = TaskService(session)
    task = await task_service.delete_task(task_id, user.id)
    return task

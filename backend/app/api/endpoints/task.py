from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.user import (
    current_user,
    customer_user,
    executor_user,
)
from app.core.db import get_async_session
from app.schemas.task import CreateTask, TaskDB
from app.models.user import User
from app.crud.task import task_crud
from app.models.task import Task
from sqlalchemy import select
from app.models.bid import Bid
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from app.services.task import TaskService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/task")


@router.post("/{task_id}/user/{executor_id}/", response_model=TaskDB, tags=["task"])
async def select_user_for_a_task(
    task_id: int,
    executor_id: int,
    user: User = Depends(customer_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Выбор исполнителя для задачи заказчиком"""
    task_service = TaskService(session)
    task = await task_service.select_user_for_task(task_id, user.id, executor_id)
    logger.info(
        f"Заказчик '{task.customer_id}' выбрал пользователя '{task.selected_executor_id}' для задачи '{task.id}'"
    )
    return task


@router.post("/create/", response_model=TaskDB, tags=["task"])
async def create_task(
    data: CreateTask,
    user: User = Depends(customer_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Создание задачи заказчиком"""
    task: Task = await task_crud.create(data, user.id, session)
    logger.info(f"Заказчик '{task.customer_id}' создал задачу '{task.id}'")
    return task


@router.get("/open/", response_model=Page[TaskDB], tags=["task"])
async def get_not_busy_tasks(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    logger.info(f"Пользователь '{user.id}' посмотрел свободные задачи")
    """Получение свободных задач, на которые еще не выбран исполнитель"""
    return await paginate(
        session,
        select(Task)
        .where(Task.selected_executor_id == None)  # noqa
        .order_by(Task.created),
    )


@router.get("/all/", response_model=Page[TaskDB], tags=["task"])
async def all(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    logger.info(f"Пользователь '{user.id}' посмотрел все задачи")
    """Получение всех задач"""
    return await paginate(session, select(Task).order_by(Task.created))


@router.get("/my_tasks/", response_model=Page[TaskDB], tags=["task"])
async def my(
    user: User = Depends(customer_user),
    session: AsyncSession = Depends(get_async_session),
):
    logger.info(f"Заказчик '{user.id}' посмотрел все свои задачи")
    """Задачи исполнителя"""
    return await paginate(
        session, select(Task).where(Task.customer_id == user.id).order_by(Task.created)
    )


@router.get("/my_responsed_tasks/", response_model=Page[TaskDB], tags=["task"])
async def my_responsed_tasks(
    user: User = Depends(executor_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Задачи, на которые откликнулся текущий исполнитель"""
    logger.info(
        f"Исполнитель '{user.id}' посмотрел все свои задачи, на которые откликнулся"
    )
    query = (
        select(Task)
        .join(Bid, Bid.task_id == Task.id)
        .where(Bid.executor_id == user.id)
        .order_by(Task.created)
    )
    return await paginate(session, query)


@router.post("/done_task_executor/{task_id}/", response_model=TaskDB, tags=["task"])
async def done_task_by_ex(
    task_id: int,
    user: User = Depends(executor_user),
    session: AsyncSession = Depends(get_async_session),
):
    task_service = TaskService(session)
    task = await task_service.done_task_by_executor(task_id, user.id)
    logger.info(
        f"Исполнитель '{task.selected_executor_id}' завершил задачу '{task.id}'"
    )
    return task


@router.post("/done_task_customer/{task_id}/", response_model=TaskDB, tags=["task"])
async def done_task_by_cus(
    task_id: int,
    user: User = Depends(customer_user),
    session: AsyncSession = Depends(get_async_session),
):
    task_service = TaskService(session)
    task = await task_service.done_task_by_customer(task_id, user)
    logger.info(
        f"Исполнитель '{task.customer_id}' подтвердил завершение задачи '{task.id}'"
    )
    return task


@router.delete("/delete/{task_id}/", response_model=TaskDB, tags=["task"])
async def cancel_task(
    task_id: int,
    user: User = Depends(customer_user),
    session: AsyncSession = Depends(get_async_session),
):
    task_service = TaskService(session)
    task = await task_service.delete_task(task_id, user.id)
    logger.info(f"Исполнитель '{task.customer_id}' удалил задачу '{task.id}'")
    return task

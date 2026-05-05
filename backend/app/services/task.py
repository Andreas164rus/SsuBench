from app.models.bid import Bid
from app.models.task import Task
from app.models.user import User
from fastapi import HTTPException, status
from app.crud.task import task_crud
from app.crud.bid import bid_crud
from app.crud.payment import payment_crud
from app.crud.user import user_crud


class TaskService:
    def __init__(self, session):
        self.session = session

    async def select_user_for_task(self, task_id, customer_id, executor_id):
        task: Task = await task_crud.get(task_id, self.session)
        if task is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Такой задачи не существует!",
            )
        if task.customer_id != customer_id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Ты не можешь выбирать исполнителя для чужой задачи!",
            )
        if task.selected_executor_id is not None:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=f"На эту задачу уже закреплен пользователь {task.selected_executor_id}!",
            )
        bid: Bid = await bid_crud.get_by_executor_id_and_task_id(
            task_id, executor_id, self.session
        )
        if bid is None or bid.executor_id != executor_id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Этот пользователь не записывался на эту задачу!",
            )

        task.selected_executor_id = executor_id
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def done_task_by_executor(self, task_id, executor_id):
        task: Task = await task_crud.get(task_id, self.session)
        if task is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Такой задачи не существует!",
            )
        if task.selected_executor_id != executor_id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Вы небраны исполнителем для этой задачи!",
            )
        task.done_executor = True
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def done_task_by_customer(self, task_id, customer: User):
        task: Task = await task_crud.get(task_id, self.session)
        if task is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Такой задачи не существует!",
            )
        if task.done_customer:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Задача уже отмечанна готовой исполнителем!",
            )
        if task.customer_id != customer.id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Вы не являетесь автором задачи!",
            )
        if not task.done_executor:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Исполнитель не завершил задачу!",
            )
        if task.price > customer.balance:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Не хватет денег для оплаты!",
            )
        await payment_crud.create(
            task.customer_id,
            task.selected_executor_id,
            task_id,
            task.price,
            self.session,
        )
        customer.balance -= task.price
        executor: User = await user_crud.get(task.selected_executor_id, self.session)
        executor.balance += task.price
        task.done_customer = True
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete_task(self, task_id, customer_id):
        task: Task = await task_crud.get(task_id, self.session)
        if task is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Такой задачи не существует!",
            )
        if task.customer_id != customer_id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Вы не являетесь автором задачи!",
            )
        if task.done_executor:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Исполнитель уже завершил задачу!",
            )

        task_deleted = await task_crud.remove(task, self.session)
        return task_deleted

    async def response_task(self, task_id, executor_id):
        task: Task = await task_crud.get(task_id, self.session)
        if task is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Такой задачи не существует!",
            )
        bid: Bid = await bid_crud.get_by_executor_id_and_task_id(
            task_id, executor_id, self.session
        )
        if bid is not None:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Отклик уже отправлен!",
            )
        bid: Bid = await bid_crud.create(task_id, executor_id, self.session)
        await self.session.commit()
        await self.session.refresh(bid)

        return bid

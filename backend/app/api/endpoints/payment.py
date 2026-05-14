from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.user import admin_user, current_user
from app.core.db import get_async_session
from app.models.user import User
from app.services.payment import PaymnetService
from app.schemas.payment import PaymnentDB, PaymnetCreate
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from app.models.payment import Payment

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payment")


@router.post(
    "/add/",
    response_model=PaymnentDB,
    tags=["payment"],
)
async def add_money_user(
    data: PaymnetCreate,
    user: User = Depends(admin_user),
    session: AsyncSession = Depends(get_async_session),
):
    admin_id = user.id
    add_balance = data.value
    add_user = data.user_id
    payment_service = PaymnetService(session)
    payment = await payment_service.add_balance(user, data)
    logger.info(
        f"Админ '{admin_id}' зачислил '{add_balance}' пользователю '{add_user}'"
    )
    return payment


@router.get(
    "/my_expenses/",
    response_model=Page[PaymnentDB],
    tags=["payment"],
)
async def get_expenses(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    logger.info(f"Пользователь '{user.id}' посмотрел свои траты")
    return await paginate(session, select(Payment).where(Payment.from_user == user.id))


@router.get(
    "/my_incoming/",
    response_model=Page[PaymnentDB],
    tags=["payment"],
)
async def get_incoming(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    logger.info(f"Пользователь '{user.id}' посмотрел свои получения")
    return await paginate(session, select(Payment).where(Payment.to_user == user.id))

from fastapi import APIRouter, Depends
from app.services.user import UserService
from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate, UserUpdateMe
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.user import current_user, admin_user
from app.crud.user import user_crud
from app.core.db import get_async_session
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


@router.patch("/users/me", response_model=UserRead, tags=["users"])
async def update_user_me(
    data: UserUpdateMe,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    logger.info(f"Пользователь '{user.id}' отредактировал себя")
    user_service = UserService(session)
    updated_user = await user_service.update_me(user, data)
    return updated_user


@router.get("/users/me", response_model=UserRead, tags=["users"])
async def info_me(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    logger.info(f"Пользователь '{user.id}' получил информацию о себе")
    u = await user_crud.get(user.id, session)
    return u


@router.patch("/users/{user_id}", response_model=UserRead, tags=["users"])
async def update_users(
    data: UserUpdate,
    user_id: int,
    user: User = Depends(admin_user),
    session: AsyncSession = Depends(get_async_session),
):
    logger.info(f"Админ '{user.id}' отредактирова пользователя '{user_id}'")
    user_service = UserService(session)
    updated_user = await user_service.update_user(user, user_id, data)
    return updated_user


@router.get("/users/{user_id}", response_model=UserRead, tags=["users"])
async def info_user(
    user_id: int,
    user: User = Depends(admin_user),
    session: AsyncSession = Depends(get_async_session),
):
    logger.info(f"Админ '{user.id}' отредактировал пользователя '{user_id}'")
    u = await user_crud.get(user_id, session)
    return u


@router.delete("/users/{user_id}", response_model=UserRead, tags=["users"])
async def deactivate_user(
    user_id: int,
    user: User = Depends(admin_user),
    session: AsyncSession = Depends(get_async_session),
):
    logger.info(f"Админ '{user.id}' деактивировал пользователя '{user_id}'")
    user_service = UserService(session)
    deleted_user = await user_service.deactivate_user(user, user_id)
    return deleted_user

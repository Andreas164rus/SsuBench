from typing import Optional, Union

from fastapi import Depends, Request
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    IntegerIDMixin,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.exceptions import UserAlreadyExists, InvalidPasswordException
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.core.config import settings
from app.core.db import get_async_session
from app.models.user import User
from app.schemas.user import UserCreate
from app.crud.role import role_crud


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:
        if len(password) < 3:
            raise InvalidPasswordException(
                reason="Password should be at least 3 characters"
            )
        if user.username in password:
            raise InvalidPasswordException(
                reason="Password should not contain username"
            )

    async def create(
        self,
        user_create: UserCreate,
        safe: bool = False,
        request: Optional[Request] = None,
    ):
        await self.validate_password(user_create.password, user_create)
        session = self.user_db.session

        existing_user = await session.execute(
            select(User).where(User.username == user_create.username)
        )
        if existing_user.scalars().first():
            raise UserAlreadyExists()

        user_dict = {
            "username": user_create.username,
            "first_name": user_create.first_name,
            "last_name": user_create.last_name,
            "hashed_password": self.password_helper.hash(user_create.password),
            "is_active": True,
            "is_superuser": False,
        }
        if not (
            user_create.username == settings.username_admin
            and user_create.password == settings.password_admin
        ):
            role_db = await role_crud.get_by_name(user_create.role_id.value, session)
            user_dict["role_id"] = role_db.id
        else:
            user_dict["is_superuser"] = True
            role_db = await role_crud.get_by_name("Админ", session)
            user_dict["role_id"] = role_db.id

        created_user = await self.user_db.create(user_dict)
        return created_user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)

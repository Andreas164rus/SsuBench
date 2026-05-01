from typing import Optional, Union

from fastapi import Depends, Request, HTTPException, status
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
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import select, func

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


class CustomUserDatabase(SQLAlchemyUserDatabase):
    async def get_by_username(self, username: str) -> Optional[User]:
        statement = select(User).where(
            func.lower(User.username) == func.lower(username)
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_by_employee_code(self, employee_code: str) -> Optional[User]:
        statement = select(User).where(User.employee_code == employee_code)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        return None


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield CustomUserDatabase(session, User)


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

    async def authenticate(
        self, credentials: OAuth2PasswordRequestForm
    ) -> Optional[User]:
        user = await self.user_db.get_by_username(credentials.username)
        if not user:
            return None
        verified, updated_hash = self.password_helper.verify_and_update(
            credentials.password, user.hashed_password
        )
        if not verified:
            return None
        return user


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)


async def customer_user(
    user: User = Depends(fastapi_users.current_user(active=True)),
) -> User:
    if user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только заказчик может делать это",
        )
    return user


async def executor_user(
    user: User = Depends(fastapi_users.current_user(active=True)),
) -> User:
    if user.role_id != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только исполнительно может делать это",
        )
    return user


current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)

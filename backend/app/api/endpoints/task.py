from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.user import auth_backend, fastapi_users, current_superuser, current_user
from app.core.db import get_async_session
from app.schemas.task import CreateTask
from app.models.user import User

router = APIRouter()


@router.post("create/", response_model=list[UserRead], tags=["users"])
async def users_by_name(
    data: CreateTask,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    # u = await user_crud.get_user_data(user.id, session)
    # if u['post_access_level'] < HR_LEVEL:
    #     return
    users = await user_crud.users_by_name(name, session)
    return users

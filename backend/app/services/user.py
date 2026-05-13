from fastapi import HTTPException, status
from app.models.user import User
from app.crud.user import user_crud
import logging

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session):
        self.session = session

    async def update_user(self, user, user_id, data):
        update_user = await user_crud.get(user_id, self.session)
        if update_user is None:
            logger.warning(
                f'Пользователь {user.id} попытался отредактировать несуществующего пользователя "{user_id}"'
            )
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Не существует такого пользователя",
            )
        if user.role_id == 3 == update_user.role_id:
            logger.warning(
                f'Пользователь {user.id} попытался отредактировать админа "{user_id}"'
            )
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Ты не можешь редактировать админа",
            )
        u = await user_crud.update(update_user, data, self.session)
        return u

    async def update_me(self, user, data):
        update_user = await user_crud.get(user.id, self.session)
        u = await user_crud.update(update_user, data, self.session)
        return u

    async def deactivate_user(self, user, user_id):
        deacivate_user: User = await user_crud.get(user_id, self.session)
        if deacivate_user is None:
            logger.warning(
                f'Пользователь {user.id} попытался деактивировать несуществующего пользователя "{user_id}"'
            )
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Не существует такого пользователя",
            )
        if user.role_id == 3 == deacivate_user.role_id:
            logger.warning(
                f'Пользователь {user.id} попытался деактивировать админа "{user_id}"'
            )
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Ты не можешь редактировать админа",
            )
        deacivate_user.is_active = False
        await self.session.commit()
        await self.session.refresh(user)
        return user

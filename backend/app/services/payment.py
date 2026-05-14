from fastapi import HTTPException, status
from app.crud.user import user_crud
from app.crud.payment import payment_crud
from app.schemas.payment import PaymnetCreate
import logging


logger = logging.getLogger(__name__)


class PaymnetService:
    def __init__(self, session):
        self.session = session

    async def add_balance(self, admin, data: PaymnetCreate):
        user = await user_crud.get(data.user_id, self.session)
        if user is None:
            logger.warning(
                f'Админ {admin.id} попытался начислить деньги несуществующему пользователя "{data.user_id}"'
            )
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Не существует такого пользователя",
            )
        payment = await payment_crud.create(
            admin.id, user.id, None, data.value, self.session
        )
        user.balance += data.value
        await self.session.commit()
        await self.session.refresh(payment)
        return payment

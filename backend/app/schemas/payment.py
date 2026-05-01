from pydantic import BaseModel


class PaymentDB(BaseModel):
    user_id: int
    task_id: int
    value: float

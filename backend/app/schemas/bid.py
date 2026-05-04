from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserRead


class BidBase(BaseModel):
    task_id: int


class CreateBid(BidBase):
    pass


class BidDB(BidBase):
    executor_id: int

    model_config = ConfigDict(from_attributes=True)


class BidWithExecutor(BidBase):
    task_id: int
    executor: UserRead

    model_config = ConfigDict(from_attributes=True)

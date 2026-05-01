from pydantic import BaseModel
from app.schemas.user import UserRead


class BidBase(BaseModel):
    task_id: int


class CreateBid(BidBase):
    pass


class BidDB(BidBase):
    executor_id: int

    class Config:
        from_attributes = True


class BidWithExecutor(BidBase):
    task_id: int
    executor: UserRead

    class Config:
        from_attributes = True

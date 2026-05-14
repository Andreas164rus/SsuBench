from pydantic import BaseModel, Field, ConfigDict


class PaymnentDB(BaseModel):
    id: int
    from_user: int
    to_user: int
    value: float
    model_config = ConfigDict(from_attributes=True)


class PaymnetCreate(BaseModel):
    user_id: int
    value: float = Field(..., gt=0)

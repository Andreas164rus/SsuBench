from sqlalchemy import Column, Integer, ForeignKey, Float
from app.core.db import Base


class Payment(Base):
    from_user = Column(Integer, ForeignKey("user.id"))
    to_user = Column(Integer, ForeignKey("user.id"))
    task_id = Column(Integer, ForeignKey("task.id"), nullable=True)
    value = Column(Float, nullable=False)

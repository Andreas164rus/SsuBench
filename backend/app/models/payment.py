from sqlalchemy import Column, Integer, ForeignKey, Float
from app.core.db import Base

class Payment(Base):
    executor_id = Column(Integer, ForeignKey("user.id"))
    customer_id = Column(Integer, ForeignKey("user.id"))
    task_id = Column(Integer, ForeignKey("task.id"))
    value = Column(Float, nullable=False)

from sqlalchemy import Column, Integer, ForeignKey, Float
from app.core.db import Base

class Payment(Base):
    user_id = Column(Integer, ForeignKey("user.id"))
    task_id = Column(Integer, ForeignKey("task.id"))
    value = Column(Float, nullable=False)

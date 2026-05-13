from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base


class Bid(Base):
    executor_id = Column(Integer, ForeignKey("user.id"))
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"))

    executor = relationship("User", foreign_keys=[executor_id])

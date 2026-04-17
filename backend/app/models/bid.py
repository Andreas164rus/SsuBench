from sqlalchemy import Column, Integer, ForeignKey, Boolean
from app.core.db import Base

class Bid(Base):
    executor_id = Column(Integer, ForeignKey("user.id"))
    task_id = Column(Integer, ForeignKey("task.id"))
    done_executor = Column(Boolean, default = False)
    done_customer = Column(Boolean, default = False)


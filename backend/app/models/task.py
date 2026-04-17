from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from app.core.db import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Task(Base):
    customer_id = Column(Integer, ForeignKey("user.id"))
    title = Column(String(length=128), nullable=False)
    describe = Column(String(length=128), nullable=False)
    price = Column(Float, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.now)

    customer = relationship("User", backref="customer_task")

    def __repr__(self):
        return f"id:{self.id}, {self.title} {self.price}"

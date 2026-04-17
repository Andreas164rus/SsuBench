from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date
from app.core.db import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    role_id = Column(Integer, ForeignKey("role.id"))
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    first_name = Column(String(length=32), nullable=False)
    last_name = Column(String(length=32), nullable=False)
    registration = Column(DateTime, nullable=False, default=datetime.now)
    role = relationship("Role", backref="user")

    def __repr__(self):
        return f"{self.first_name} {self.last_name}, id: {self.id}, role; {self.role}"

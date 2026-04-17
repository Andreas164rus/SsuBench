from sqlalchemy import Column, String
# from sqlalchemy.orm import relationship

from app.core.db import Base


class Role(Base):
    name = Column(String, unique=True, default='customer')

    def __repr__(self):
        return (f"{self.name}")
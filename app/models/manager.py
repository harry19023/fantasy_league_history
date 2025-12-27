from sqlalchemy import Column, Integer, String

from app.database import Base


class Manager(Base):
    __tablename__ = "manager"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)

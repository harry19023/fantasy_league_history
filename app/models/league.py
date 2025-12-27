from sqlalchemy import JSON, Column, Integer, String

from app.database import Base


class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    settings = Column(JSON, nullable=True)

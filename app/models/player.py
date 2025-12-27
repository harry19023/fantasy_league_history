from sqlalchemy import Column, Integer, String

from app.database import Base


class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    position = Column(String, nullable=False)
    nfl_team = Column(String, nullable=True)  # NFL team they play for

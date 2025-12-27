from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    week = Column(Integer, nullable=False)
    game_type = Column(
        String, nullable=False
    )  # "REGULAR", "PLAYOFF_WINNERS", "PLAYOFF_LOSERS"
    franchise1_id = Column(Integer, ForeignKey("franchises.id"), nullable=False)
    franchise2_id = Column(Integer, ForeignKey("franchises.id"), nullable=False)
    franchise1_score = Column(Float, nullable=True)
    franchise2_score = Column(Float, nullable=True)
    game_date = Column(Date, nullable=True)

    # Relationships
    season = relationship("Season", backref="games")
    franchise1 = relationship(
        "Franchise", foreign_keys=[franchise1_id], backref="games_as_franchise1"
    )
    franchise2 = relationship(
        "Franchise", foreign_keys=[franchise2_id], backref="games_as_franchise2"
    )

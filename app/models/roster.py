from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Roster(Base):
    __tablename__ = "rosters"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    week = Column(Integer, nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)

    # Relationships
    team = relationship("Team", backref="rosters")
    player = relationship("Player", backref="rosters")

    # Ensure unique player per team per week
    __table_args__ = (
        UniqueConstraint(
            "team_id", "week", "player_id", name="unique_team_week_player"
        ),
    )

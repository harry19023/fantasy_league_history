from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class Matchup(Base):
    __tablename__ = "matchups"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    week = Column(Integer, nullable=False)
    team1_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    team2_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    team1_score = Column(Float, nullable=True)
    team2_score = Column(Float, nullable=True)

    # Relationships
    league = relationship("League", backref="matchups")
    team1 = relationship("Team", foreign_keys=[team1_id], backref="matchups_as_team1")
    team2 = relationship("Team", foreign_keys=[team2_id], backref="matchups_as_team2")

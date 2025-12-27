from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Franchise(Base):
    __tablename__ = "franchise"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("league.id"), nullable=False)
    name = Column(String, nullable=False)

    # Relationships
    league = relationship("League", backref="franchises")

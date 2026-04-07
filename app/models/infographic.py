from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Infographic(Base):
    __tablename__ = "infographics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    data = Column(String, nullable=False) # JSON payload string
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="infographics")

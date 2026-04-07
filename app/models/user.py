from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    tier = Column(String, default="Free")
    usage_count = Column(Integer, default=0)
    limit_month = Column(Integer, default=10)

    infographics = relationship("Infographic", back_populates="user")

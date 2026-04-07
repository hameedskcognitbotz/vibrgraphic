from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from app.core.database import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True) # Assuming User logic can be added later
    topic = Column(String, nullable=False)
    audience = Column(String, nullable=True, default="general") # creator, educator, general
    format = Column(String, nullable=True, default="infographic") # infographic, carousel
    tone = Column(String, nullable=True, default="Educational")
    status = Column(String, default="pending") # pending, processing, completed, failed
    result_url = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from .base import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # summarize, outline, draft, export
    status = Column(String, nullable=False)  # queued, running, success, failed
    payload = Column(Text)  # JSON payload
    result = Column(Text)  # JSON result
    error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

from sqlalchemy import Column, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class JobAttempt(Base):
    __tablename__ = "job_attempts"

    job_id = Column(String, ForeignKey("pipeline_jobs.id"), nullable=False)
    attempt_no = Column(Integer, nullable=False)
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    error_json = Column(JSON)

    # Relationships
    job = relationship("PipelineJob", back_populates="attempts")

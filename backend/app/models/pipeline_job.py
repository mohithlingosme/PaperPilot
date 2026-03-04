from sqlalchemy import Column, String, Integer, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import enum

class JobStatus(enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobType(enum.Enum):
    SUMMARIZE = "summarize"
    OUTLINE = "outline"
    DRAFT = "draft"
    EXPORT = "export"
    OCR = "ocr"

class PipelineJob(Base):
    __tablename__ = "pipeline_jobs"

    type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.QUEUED)
    priority = Column(Integer, nullable=False, default=0)
    payload = Column(Text)  # JSON payload

    # Foreign Keys
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    source_id = Column(String, ForeignKey("sources.id"))

    # Relationships
    workspace = relationship("Workspace")
    project = relationship("Project", back_populates="pipeline_jobs")
    source = relationship("Source")
    attempts = relationship("JobAttempt", back_populates="job", cascade="all, delete-orphan", order_by="JobAttempt.attempt_no")

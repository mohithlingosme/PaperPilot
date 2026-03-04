from sqlalchemy import Column, String, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import enum

class SourceType(enum.Enum):
    PDF = "pdf"
    URL = "url"
    TEXT = "text"

class Source(Base):
    __tablename__ = "sources"

    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    type = Column(Enum(SourceType), nullable=False)
    title = Column(String, nullable=False)
    metadata = Column(JSON)  # Additional metadata like URL, file size, etc.

    # Relationships
    workspace = relationship("Workspace", back_populates="sources")
    project = relationship("Project", back_populates="sources")
    versions = relationship("SourceVersion", back_populates="source", cascade="all, delete-orphan")
    pipeline_jobs = relationship("PipelineJob", back_populates="source", cascade="all, delete-orphan")

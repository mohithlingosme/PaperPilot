from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Project(Base):
    __tablename__ = "projects"

    name = Column(String, nullable=False)
    description = Column(Text)

    # Foreign Keys
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="projects")
    sources = relationship("Source", back_populates="project", cascade="all, delete-orphan")
    pipeline_jobs = relationship("PipelineJob", back_populates="project", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="project", cascade="all, delete-orphan")
    drafts = relationship("Draft", back_populates="project", cascade="all, delete-orphan")

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Draft(Base):
    __tablename__ = "drafts"

    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    # Foreign Keys
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)

    # Relationships
    workspace = relationship("Workspace")
    project = relationship("Project", back_populates="drafts")
    versions = relationship("DraftVersion", back_populates="draft", cascade="all, delete-orphan", order_by="DraftVersion.created_at")
    citations = relationship("Citation", back_populates="draft", cascade="all, delete-orphan")
    exports = relationship("Export", back_populates="draft", cascade="all, delete-orphan")

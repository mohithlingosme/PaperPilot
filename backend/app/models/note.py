from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Note(Base):
    __tablename__ = "notes"

    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    # Foreign Keys
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)

    # Relationships
    workspace = relationship("Workspace")
    project = relationship("Project", back_populates="notes")
    versions = relationship("NoteVersion", back_populates="note", cascade="all, delete-orphan", order_by="NoteVersion.created_at")

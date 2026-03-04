from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class NoteVersion(Base):
    __tablename__ = "note_versions"

    note_id = Column(String, ForeignKey("notes.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    # Relationships
    note = relationship("Note", back_populates="versions")

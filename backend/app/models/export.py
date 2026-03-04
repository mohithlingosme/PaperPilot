from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import enum

class ExportStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Export(Base):
    __tablename__ = "exports"

    draft_version_id = Column(String, ForeignKey("draft_versions.id"), nullable=False)
    format = Column(String, nullable=False)  # pdf, docx, html, etc.
    status = Column(Enum(ExportStatus), nullable=False, default=ExportStatus.PENDING)

    # Relationships
    draft_version = relationship("DraftVersion", back_populates="exports")
    files = relationship("ExportFile", back_populates="export", cascade="all, delete-orphan")

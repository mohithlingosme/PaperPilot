from sqlalchemy import Column, Integer, Text, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base

class SourcePage(Base):
    __tablename__ = "source_pages"

    page_no = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    ocr_status = Column(String, nullable=False, default="pending")  # pending, completed, failed

    # Foreign Keys
    source_version_id = Column(String, ForeignKey("source_versions.id"), nullable=False)

    # Relationships
    source_version = relationship("SourceVersion", back_populates="pages")
    spans = relationship("SourceSpan", back_populates="page", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('page_no > 0', name='check_page_no_positive'),
    )

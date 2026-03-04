from sqlalchemy import Column, Integer, Text, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base

class SourceSpan(Base):
    __tablename__ = "source_spans"

    page_id = Column(String, ForeignKey("source_pages.id"), nullable=False)
    start_offset = Column(Integer, nullable=False)
    end_offset = Column(Integer, nullable=False)
    snippet = Column(Text, nullable=False)

    # Relationships
    page = relationship("SourcePage", back_populates="spans")
    citations = relationship("Citation", back_populates="source_span", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('start_offset >= 0', name='check_start_offset_non_negative'),
        CheckConstraint('end_offset > start_offset', name='check_end_offset_greater_than_start'),
    )

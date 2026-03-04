class Citation(Base):
    __tablename__ = "citations"
=======
from sqlalchemy import Column, Text, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class Citation(Base):
    __tablename__ = "citations"

    quote = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False, default=1.0)

    # Foreign Keys
    draft_version_id = Column(String, ForeignKey("draft_versions.id"), nullable=False)
    source_span_id = Column(String, ForeignKey("source_spans.id"), nullable=False)

    # Relationships
    draft_version = relationship("DraftVersion", back_populates="citations")
    source_span = relationship("SourceSpan", back_populates="citations")

    __table_args__ = (
        UniqueConstraint('draft_version_id', 'source_span_id', name='unique_draft_version_source_span'),
    )

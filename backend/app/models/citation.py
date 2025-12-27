from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from .base import Base

class Citation(Base):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("drafts.id"), nullable=False)
    chunk_id = Column(Integer, ForeignKey("source_chunks.id"), nullable=False)
    style = Column(String, nullable=False)  # APA, MLA, etc.
    page_locator = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

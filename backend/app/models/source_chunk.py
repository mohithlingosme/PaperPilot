from sqlalchemy import Column, Integer, String, Text, Integer, String, ARRAY, DateTime, func, ForeignKey, Float
from .base import Base

class SourceChunk(Base):
    __tablename__ = "source_chunks"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    text = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    page_no = Column(Integer)
    heading_path = Column(String)
    embedding = Column(ARRAY(Float))  # Assuming vector extension for embeddings
    created_at = Column(DateTime(timezone=True), server_default=func.now())

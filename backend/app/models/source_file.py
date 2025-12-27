from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func, ForeignKey
from .base import Base

class SourceFile(Base):
    __tablename__ = "source_files"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    storage_path = Column(String, nullable=False)
    hash = Column(String, nullable=False)
    size = Column(BigInteger, nullable=False)
    mime_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

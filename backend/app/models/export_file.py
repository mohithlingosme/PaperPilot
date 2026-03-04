from sqlalchemy import Column, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ExportFile(Base):
    __tablename__ = "export_files"

    storage_provider = Column(String, nullable=False)  # s3, gcs, local
    bucket = Column(String, nullable=False)
    object_key = Column(String, nullable=False)
    checksum = Column(String, nullable=False)
    size = Column(BigInteger, nullable=False)
    mime_type = Column(String, nullable=False)

    # Foreign Keys
    export_id = Column(String, ForeignKey("exports.id"), nullable=False)

    # Relationships
    export = relationship("Export", back_populates="files")

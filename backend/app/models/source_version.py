from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base

class SourceVersion(Base):
    __tablename__ = "source_versions"

    version_no = Column(Integer, nullable=False)
    checksum = Column(String, nullable=False)

    # Foreign Keys
    source_id = Column(String, ForeignKey("sources.id"), nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)

    # Relationships
    source = relationship("Source", back_populates="versions")
    creator = relationship("User")
    files = relationship("SourceFile", back_populates="source_version", cascade="all, delete-orphan")
    pages = relationship("SourcePage", back_populates="source_version", cascade="all, delete-orphan", order_by="SourcePage.page_no")

    __table_args__ = (
        CheckConstraint('version_no > 0', name='check_version_no_positive'),
    )

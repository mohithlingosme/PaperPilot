from sqlalchemy import Column, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class UsageEvent(Base):
    __tablename__ = "usage_events"

    type = Column(String, nullable=False)  # ocr_pages, tokens, api_calls, etc.
    amount = Column(Float, nullable=False)
    meta = Column(Text)  # JSON metadata

    # Foreign Keys
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)

    # Relationships
    workspace = relationship("Workspace")

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ApiKey(Base):
    __tablename__ = "api_keys"

    key_hash = Column(String, nullable=False, unique=True, index=True)
    last_used_at = Column(DateTime(timezone=True))

    # Foreign Keys
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    workspace_id = Column(String, ForeignKey("workspaces.id"))

    # Relationships
    user = relationship("User", back_populates="api_keys")
    workspace = relationship("Workspace", back_populates="api_keys")

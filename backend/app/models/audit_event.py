from sqlalchemy import Column, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class AuditEvent(Base):
    __tablename__ = "audit_events"

    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    actor_user_id = Column(String, ForeignKey("users.id"))
    action = Column(String, nullable=False)  # create, update, delete, etc.
    entity_type = Column(String, nullable=False)  # user, workspace, project, etc.
    entity_id = Column(String, nullable=False)
    payload = Column(JSON)  # Additional context data

    # Relationships
    workspace = relationship("Workspace", back_populates="audit_events")
    actor_user = relationship("User", back_populates="audit_events")

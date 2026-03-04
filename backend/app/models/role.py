from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import Base
import enum

class RoleName(enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class Role(Base):
    __tablename__ = "roles"

    name = Column(String, nullable=False, unique=True)

    # Relationships
    workspace_members = relationship("WorkspaceMember", back_populates="role")

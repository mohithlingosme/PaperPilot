from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import Base

class Workspace(Base):
    __tablename__ = "workspaces"

    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)

    # Relationships
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="workspace", cascade="all, delete-orphan")

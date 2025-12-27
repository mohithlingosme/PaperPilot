import pytest
from backend.app.models.account import User
from backend.app.models.base import Base

def test_user_model(db_session):
    """Test User model creation and basic functionality."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    retrieved = db_session.query(User).filter_by(email="test@example.com").first()
    assert retrieved is not None
    assert retrieved.email == "test@example.com"
    assert retrieved.is_active == True

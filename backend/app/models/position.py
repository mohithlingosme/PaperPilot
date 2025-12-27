from sqlalchemy import Column, Integer, String, Numeric, DateTime, func, Index
from .base import Base

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    account_id = Column(Integer, nullable=False, index=True)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # LONG or SHORT
    qty = Column(Numeric(18, 6), nullable=False)
    avg_entry = Column(Numeric(18, 6), nullable=False)
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_positions_user_symbol', 'user_id', 'symbol'),
    )

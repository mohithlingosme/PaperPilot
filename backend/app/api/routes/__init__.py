"""
API route handlers for PaperPilot.
"""

from .trading import router as trading_router

__all__ = ["trading_router"]

Backwards-compatible indicators module.

This module provides backwards compatibility by re-exporting all indicators.
For new code, import directly from finbot.indicators instead.
"""

# Re-export all indicators for backwards compatibility
from .indicators import *

__all__ = [
    'Indicator',
    'SMA',
    'RSI',
]
=======
"""
Backwards-compatible indicators module.

This module provides backwards compatibility by re-exporting all indicators.
For new code, import directly from finbot.indicators instead.
"""

# Re-export all indicators for backwards compatibility
from .indicators.base import Indicator
from .indicators.sma import SMA
from .indicators.rsi import RSI

__all__ = [
    'Indicator',
    'SMA',
    'RSI',
]

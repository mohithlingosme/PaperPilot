"""
Trading Strategy Interface

Defines the base strategy class and interfaces for trading signals.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Signal(Enum):
    """Trading signals."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class Order:
    """Order representation."""
    symbol: str
    side: str  # BUY or SELL
    quantity: float
    price: Optional[float] = None  # Market order if None
    order_type: str = "MARKET"
    timestamp: Optional[float] = None


class Strategy(ABC):
    """
    Abstract base class for trading strategies.

    Strategies implement on_bar() or on_tick() methods to generate trading signals.
    """

    def __init__(self, name: str, logger: Optional[logging.Logger] = None):
        self.name = name
        self.logger = logger or logging.getLogger(f"{self.__class__.__name__}")

    @abstractmethod
    def on_bar(self, bar: Dict[str, Any]) -> Optional[Order]:
        """
        Called on each new bar/candlestick.

        Args:
            bar: OHLCV data for the current bar

        Returns:
            Order to execute, or None for no action
        """
        pass

    def on_tick(self, tick: Dict[str, Any]) -> Optional[Order]:
        """
        Called on each new tick (optional implementation).

        Args:
            tick: Tick data

        Returns:
            Order to execute, or None for no action
        """
        return None

    def generate_signal(self, data: Dict[str, Any]) -> Signal:
        """
        Generate a trading signal from market data.

        Args:
            data: Market data (bar or tick)

        Returns:
            Trading signal
        """
        # Default implementation - override in subclasses
        return Signal.HOLD

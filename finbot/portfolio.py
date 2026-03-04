"""
Portfolio Management

Handles cash, positions, and P&L bookkeeping.
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Position:
    """Represents a trading position."""
    symbol: str
    quantity: float
    avg_entry_price: float
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    opened_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def update_pnl(self, current_price: float) -> None:
        """Update unrealized P&L based on current price."""
        self.current_price = current_price
        self.unrealized_pnl = (current_price - self.avg_entry_price) * self.quantity
        self.updated_at = datetime.now()

    def close_position(self, exit_price: float, quantity: Optional[float] = None) -> float:
        """
        Close position (fully or partially).

        Args:
            exit_price: Price at which to close
            quantity: Quantity to close (None for full position)

        Returns:
            Realized P&L from the closure
        """
        close_qty = quantity if quantity is not None else self.quantity
        pnl = (exit_price - self.avg_entry_price) * close_qty

        self.realized_pnl += pnl
        self.quantity -= close_qty

        # If position is fully closed, reset unrealized P&L
        if abs(self.quantity) < 1e-8:
            self.unrealized_pnl = 0.0

        self.updated_at = datetime.now()
        return pnl


class Portfolio:
    """
    Portfolio management system.
    """

    def __init__(self, initial_cash: float = 100000.0, logger: Optional[logging.Logger] = None):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.logger = logger or logging.getLogger(f"{self.__class__.__name__}")

    @property
    def equity(self) -> float:
        """Total equity (cash + position values)."""
        position_value = sum(
            abs(pos.quantity * pos.current_price) for pos in self.positions.values()
        )
        return self.cash + position_value

    @property
    def total_pnl(self) -> float:
        """Total P&L (realized + unrealized)."""
        realized = sum(pos.realized_pnl for pos in self.positions.values())
        unrealized = sum(pos.unrealized_pnl for pos in self.positions.values())
        return realized + unrealized

    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a symbol."""
        return self.positions.get(symbol)

    def update_price(self, symbol: str, price: float) -> None:
        """Update price for a symbol and recalculate P&L."""
        if symbol in self.positions:
            self.positions[symbol].update_pnl(price)

    def can_afford(self, symbol: str, quantity: float, price: float) -> bool:
        """
        Check if portfolio can afford a trade.

        Args:
            symbol: Trading symbol
            quantity: Trade quantity
            price: Trade price

        Returns:
            True if trade is affordable
        """
        cost = abs(quantity * price)

        # For buys, check cash
        if quantity > 0:
            return self.cash >= cost

        # For sells, check if position exists and is large enough
        position = self.get_position(symbol)
        if not position:
            return False
        return position.quantity >= abs(quantity)

    def execute_trade(self, symbol: str, quantity: float, price: float) -> bool:
        """
        Execute a trade (internal method - use with risk management).

        Args:
            symbol: Trading symbol
            quantity: Trade quantity (positive for buy, negative for sell)
            price: Trade price

        Returns:
            True if trade executed successfully
        """
        if not self.can_afford(symbol, quantity, price):
            self.logger.warning(f"Cannot afford trade: {symbol} {quantity} @ {price}")
            return False

        cost = quantity * price

        if quantity > 0:  # Buy
            self.cash -= cost
            if symbol in self.positions:
                # Average down/up the entry price
                existing_pos = self.positions[symbol]
                total_qty = existing_pos.quantity + quantity
                total_cost = (existing_pos.quantity * existing_pos.avg_entry_price) + cost
                new_avg_price = total_cost / total_qty
                existing_pos.quantity = total_qty
                existing_pos.avg_entry_price = new_avg_price
                existing_pos.update_pnl(price)
            else:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=quantity,
                    avg_entry_price=price,
                    current_price=price
                )
        else:  # Sell
            self.cash -= cost  # cost is negative for sells
            position = self.positions.get(symbol)
            if position:
                realized_pnl = position.close_position(price, abs(quantity))
                self.logger.info(f"Closed position {symbol}: P&L = {realized_pnl}")

                # Remove position if fully closed
                if abs(position.quantity) < 1e-8:
                    del self.positions[symbol]

        self.logger.info(f"Executed trade: {symbol} {quantity} @ {price}, Cash: {self.cash}")
        return True

    def get_summary(self) -> Dict[str, float]:
        """Get portfolio summary."""
        return {
            'cash': self.cash,
            'equity': self.equity,
            'total_pnl': self.total_pnl,
            'positions_count': len(self.positions)
        }

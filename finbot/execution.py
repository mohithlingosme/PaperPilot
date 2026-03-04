"""
Execution Engine

Simulates order execution and fill generation for paper trading.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from .portfolio import Portfolio
from .risk import RiskManager


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class Fill:
    """Represents a trade execution."""
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    timestamp: float
    commission: float = 0.0


@dataclass
class Order:
    """Trading order."""
    id: str
    symbol: str
    side: str  # BUY or SELL
    quantity: float
    price: Optional[float] = None  # None for market orders
    order_type: str = "MARKET"
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    remaining_quantity: float = 0.0
    fills: List[Fill] = None
    created_at: float = 0.0

    def __post_init__(self):
        if self.fills is None:
            self.fills = []
        self.remaining_quantity = self.quantity
        if not self.created_at:
            self.created_at = time.time()


class ExecutionEngine:
    """
    Simulates order execution for paper trading/backtesting.
    """

    def __init__(self,
                 portfolio: Portfolio,
                 risk_manager: Optional[RiskManager] = None,
                 logger: Optional[logging.Logger] = None):
        self.portfolio = portfolio
        self.risk_manager = risk_manager
        self.logger = logger or logging.getLogger(f"{self.__class__.__name__}")
        self.pending_orders: Dict[str, Order] = {}
        self.completed_orders: Dict[str, Order] = {}
        self.fills: List[Fill] = []

    def submit_order(self,
                    symbol: str,
                    side: str,
                    quantity: float,
                    price: Optional[float] = None,
                    order_type: str = "MARKET") -> Optional[str]:
        """
        Submit an order for execution.

        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
            price: Limit price (None for market orders)
            order_type: Order type

        Returns:
            Order ID if accepted, None if rejected
        """
        # Create order
        order_id = f"order_{int(time.time() * 1000000)}"
        order = Order(
            id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            order_type=order_type
        )

        # Risk check
        effective_price = price if price is not None else self._get_last_price(symbol)

        if self.risk_manager:
            if not self.risk_manager.validate_order(
                self.portfolio,
                symbol,
                quantity if side == "BUY" else -quantity,
                effective_price
            ):
                order.status = OrderStatus.REJECTED
                self.completed_orders[order_id] = order
                self.logger.warning(f"Order {order_id} rejected by risk manager")
                return None

        # Accept order
        self.pending_orders[order_id] = order
        self.logger.info(f"Order {order_id} submitted: {side} {quantity} {symbol}")
        return order_id

    def execute_pending_orders(self, market_data: Dict[str, Any]) -> List[Fill]:
        """
        Execute all pending orders based on current market data.

        Args:
            market_data: Current market prices and data

        Returns:
            List of fills generated
        """
        fills = []

        for order_id, order in list(self.pending_orders.items()):
            fill = self._execute_order(order, market_data)
            if fill:
                fills.append(fill)
                self.fills.append(fill)

                # Update order status
                order.filled_quantity += fill.quantity
                order.remaining_quantity -= fill.quantity
                order.fills.append(fill)

                if order.remaining_quantity <= 0:
                    order.status = OrderStatus.FILLED
                    self.completed_orders[order_id] = order
                    del self.pending_orders[order_id]
                else:
                    order.status = OrderStatus.PARTIAL

        return fills

    def _get_last_price(self, symbol: str) -> float:
        """Best-effort price for risk checks when no explicit price is provided."""
        position = self.portfolio.get_position(symbol)
        if position and position.current_price:
            return position.current_price
        return 0.0

    def _execute_order(self, order: Order, market_data: Dict[str, Any]) -> Optional[Fill]:
        """
        Execute a single order.

        Args:
            order: Order to execute
            market_data: Current market data

        Returns:
            Fill if executed, None otherwise
        """
        symbol = order.symbol

        # Get execution price
        if order.order_type == "MARKET":
            # Use current market price
            if 'close' in market_data:
                exec_price = market_data['close']
            elif symbol in market_data:
                exec_price = market_data[symbol]
            else:
                self.logger.warning(f"No price data for {symbol}")
                return None
        elif order.order_type == "LIMIT":
            # Check if limit can be filled
            if order.price is None:
                return None

            if 'close' in market_data:
                market_price = market_data['close']
            elif symbol in market_data:
                market_price = market_data[symbol]
            else:
                return None

            # For simplicity, assume limit orders fill immediately at limit price
            # In reality, this would depend on order book
            if (order.side == "BUY" and market_price <= order.price) or \
               (order.side == "SELL" and market_price >= order.price):
                exec_price = order.price
            else:
                return None
        else:
            self.logger.warning(f"Unsupported order type: {order.order_type}")
            return None

        # Calculate commission (simplified)
        commission = abs(order.remaining_quantity * exec_price) * 0.001  # 0.1% commission

        # Create fill
        fill = Fill(
            order_id=order.id,
            symbol=symbol,
            side=order.side,
            quantity=min(order.remaining_quantity, order.quantity),  # Fill remaining
            price=exec_price,
            timestamp=time.time(),
            commission=commission
        )

        # Update portfolio
        trade_quantity = fill.quantity if order.side == "BUY" else -fill.quantity
        success = self.portfolio.execute_trade(symbol, trade_quantity, exec_price)

        if not success:
            self.logger.error(f"Portfolio update failed for order {order.id}")
            return None

        self.logger.info(f"Fill: {fill.side} {fill.quantity} {fill.symbol} @ {fill.price}")
        return fill

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a pending order.

        Args:
            order_id: Order ID to cancel

        Returns:
            True if cancelled successfully
        """
        if order_id in self.pending_orders:
            order = self.pending_orders[order_id]
            order.status = OrderStatus.CANCELLED
            self.completed_orders[order_id] = order
            del self.pending_orders[order_id]
            self.logger.info(f"Order {order_id} cancelled")
            return True

        return False

    def get_order_status(self, order_id: str) -> Optional[Order]:
        """Get order status by ID."""
        if order_id in self.pending_orders:
            return self.pending_orders[order_id]
        return self.completed_orders.get(order_id)

    def get_all_orders(self) -> List[Order]:
        """Get all orders (pending and completed)."""
        return list(self.pending_orders.values()) + list(self.completed_orders.values())

    def get_fills(self, order_id: Optional[str] = None) -> List[Fill]:
        """
        Get fills, optionally filtered by order ID.

        Args:
            order_id: Specific order ID to filter by

        Returns:
            List of fills
        """
        if order_id:
            return [f for f in self.fills if f.order_id == order_id]
        return self.fills.copy()

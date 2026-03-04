"""
Trading Engine

Brings together strategy, portfolio, risk management, and execution.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from .strategy import Strategy, Order
from .portfolio import Portfolio
from .risk import RiskManager
from .execution import ExecutionEngine, Fill


class TradingEngine:
    """
    Main trading engine that orchestrates strategy execution.
    """

    def __init__(self,
                 strategy: Strategy,
                 portfolio: Portfolio,
                 risk_manager: Optional[RiskManager] = None,
                 logger: Optional[logging.Logger] = None):
        self.strategy = strategy
        self.portfolio = portfolio
        self.risk_manager = risk_manager or RiskManager()
        self.execution_engine = ExecutionEngine(portfolio, risk_manager)
        self.logger = logger or logging.getLogger(f"{self.__class__.__name__}")

        # Set initial equity for risk manager
        self.risk_manager.set_initial_equity(portfolio.equity)

    def process_bar(self, bar: Dict[str, Any]) -> List[Fill]:
        """
        Process a new bar/candlestick.

        Args:
            bar: OHLCV data for the current bar

        Returns:
            List of fills generated
        """
        # Update portfolio prices
        if 'symbol' in bar:
            symbol = bar['symbol']
            price = bar.get('close', bar.get('price', 0))
            self.portfolio.update_price(symbol, price)

        # Generate signal from strategy
        order = self.strategy.on_bar(bar)

        fills = []

        if order:
            # Submit order
            order_id = self.execution_engine.submit_order(
                order.symbol, order.side, order.quantity, order.price, order.order_type
            )

            if order_id:
                self.logger.info(f"Strategy {self.strategy.name} generated order: {order.side} {order.quantity} {order.symbol}")

                # Execute pending orders
                market_data = {order.symbol: bar.get('close', bar.get('price', 0))}
                fills = self.execution_engine.execute_pending_orders(market_data)

                # Log fills
                for fill in fills:
                    self.logger.info(f"Fill executed: {fill.side} {fill.quantity} {fill.symbol} @ {fill.price}")
            else:
                self.logger.warning(f"Order rejected: {order.side} {order.quantity} {order.symbol}")

        return fills

    def process_tick(self, tick: Dict[str, Any]) -> List[Fill]:
        """
        Process a new tick (for high-frequency strategies).

        Args:
            tick: Tick data

        Returns:
            List of fills generated
        """
        # Update portfolio prices
        if 'symbol' in tick:
            symbol = tick['symbol']
            price = tick.get('price', 0)
            self.portfolio.update_price(symbol, price)

        # Generate signal from strategy
        order = self.strategy.on_tick(tick)

        fills = []

        if order:
            order_id = self.execution_engine.submit_order(
                order.symbol, order.side, order.quantity, order.price, order.order_type
            )

            if order_id:
                market_data = {order.symbol: tick.get('price', 0)}
                fills = self.execution_engine.execute_pending_orders(market_data)

        return fills

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get current portfolio summary."""
        summary = self.portfolio.get_summary()
        summary.update({
            'strategy': self.strategy.name,
            'pending_orders': len(self.execution_engine.pending_orders),
            'completed_orders': len(self.execution_engine.completed_orders),
            'total_fills': len(self.execution_engine.fills)
        })
        return summary

    def stop(self) -> None:
        """Stop the trading engine and cancel all pending orders."""
        for order_id in list(self.execution_engine.pending_orders.keys()):
            self.execution_engine.cancel_order(order_id)

        self.logger.info("Trading engine stopped")

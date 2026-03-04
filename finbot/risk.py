"""
Risk Management

Position sizing, max exposure, drawdown guards.
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from .portfolio import Portfolio


@dataclass
class RiskLimits:
    """Risk limits configuration."""
    max_position_size_pct: float = 0.2  # Max 20% of equity per position
    max_total_exposure_pct: float = 0.8  # Max 80% of equity in total
    max_loss_pct: float = 0.1  # Max 10% loss before stopping
    max_drawdown_pct: float = 0.2  # Max 20% drawdown
    min_cash_reserve_pct: float = 0.1  # Keep at least 10% cash


class RiskManager:
    """
    Risk management system for trading.
    
    Validates orders against risk limits before execution.
    """

    def __init__(self,
                 max_position_size_pct: float = 0.2,
                 max_total_exposure_pct: float = 0.8,
                 max_loss_pct: float = 0.1,
                 max_drawdown_pct: float = 0.2,
                 min_cash_reserve_pct: float = 0.1,
                 logger: Optional[logging.Logger] = None):
        self.limits = RiskLimits(
            max_position_size_pct=max_position_size_pct,
            max_total_exposure_pct=max_total_exposure_pct,
            max_loss_pct=max_loss_pct,
            max_drawdown_pct=max_drawdown_pct,
            min_cash_reserve_pct=min_cash_reserve_pct
        )
        self.initial_equity: float = 100000.0
        self.logger = logger or logging.getLogger(f"{self.__class__.__name__}")
        self.trading_paused: bool = False

    def set_initial_equity(self, equity: float) -> None:
        """Set initial equity for drawdown calculations."""
        self.initial_equity = equity
        self.logger.info(f"Initial equity set to {equity}")

    def validate_order(self,
                      portfolio: Portfolio,
                      symbol: str,
                      quantity: float,
                      price: float) -> bool:
        """
        Validate an order against risk limits.

        Args:
            portfolio: Current portfolio state
            symbol: Trading symbol
            quantity: Order quantity (positive for buy, negative for sell)
            price: Order price

        Returns:
            True if order passes risk checks, False otherwise
        """
        # Check if trading is paused
        if self.trading_paused:
            self.logger.warning("Trading is paused due to risk limits")
            return False

        # Check drawdown
        if self._check_drawdown_limit(portfolio):
            self.logger.warning("Drawdown limit exceeded - trading paused")
            self.trading_paused = True
            return False

        # Check loss limit
        if self._check_loss_limit(portfolio):
            self.logger.warning("Loss limit exceeded - trading paused")
            self.trading_paused = True
            return False

        # For sell orders, just validate position exists
        if quantity < 0:
            position = portfolio.get_position(symbol)
            if not position or position.quantity < abs(quantity):
                self.logger.warning(f"Insufficient position to sell: {symbol}")
                return False
            return True

        # For buy orders, validate position size and exposure
        trade_value = abs(quantity * price)
        equity = portfolio.equity

        # Check position size limit
        position_pct = trade_value / equity
        if position_pct > self.limits.max_position_size_pct:
            self.logger.warning(
                f"Position size {position_pct:.2%} exceeds limit {self.limits.max_position_size_pct:.2%}"
            )
            return False

        # Calculate new total exposure
        current_exposure = self._calculate_total_exposure(portfolio)
        new_exposure = current_exposure + trade_value
        new_exposure_pct = new_exposure / equity

        # Check total exposure limit
        if new_exposure_pct > self.limits.max_total_exposure_pct:
            self.logger.warning(
                f"Total exposure {new_exposure_pct:.2%} exceeds limit {self.limits.max_total_exposure_pct:.2%}"
            )
            return False

        # Check cash reserve
        new_cash = portfolio.cash - trade_value
        cash_reserve_pct = new_cash / equity
        if cash_reserve_pct < self.limits.min_cash_reserve_pct:
            self.logger.warning(
                f"Cash reserve {cash_reserve_pct:.2%} below minimum {self.limits.min_cash_reserve_pct:.2%}"
            )
            return False

        self.logger.info(f"Order validated: {symbol} {quantity} @ {price}")
        return True

    def _calculate_total_exposure(self, portfolio: Portfolio) -> float:
        """Calculate total exposure (value of all positions)."""
        exposure = 0.0
        for position in portfolio.positions.values():
            exposure += abs(position.quantity * position.current_price)
        return exposure

    def _check_drawdown_limit(self, portfolio: Portfolio) -> bool:
        """Check if drawdown exceeds limit."""
        if self.initial_equity <= 0:
            return False

        current_equity = portfolio.equity
        drawdown = (self.initial_equity - current_equity) / self.initial_equity

        return drawdown >= self.limits.max_drawdown_pct

    def _check_loss_limit(self, portfolio: Portfolio) -> bool:
        """Check if loss exceeds limit."""
        if self.initial_equity <= 0:
            return False

        current_equity = portfolio.equity
        loss_pct = (self.initial_equity - current_equity) / self.initial_equity

        return loss_pct >= self.limits.max_loss_pct

    def calculate_position_size(self,
                                portfolio: Portfolio,
                                price: float,
                                stop_loss_pct: Optional[float] = None) -> float:
        """
        Calculate recommended position size based on risk limits.

        Args:
            portfolio: Current portfolio
            price: Entry price
            stop_loss_pct: Optional stop loss percentage for risk-based sizing

        Returns:
            Recommended quantity to buy
        """
        equity = portfolio.equity

        # Start with max position size
        max_value = equity * self.limits.max_position_size_pct

        # Adjust for cash reserve
        min_cash = equity * self.limits.min_cash_reserve_pct
        available_cash = portfolio.cash - min_cash
        max_value = min(max_value, available_cash)

        # Adjust for total exposure
        current_exposure = self._calculate_total_exposure(portfolio)
        max_exposure = equity * self.limits.max_total_exposure_pct
        remaining_exposure = max(0, max_exposure - current_exposure)
        max_value = min(max_value, remaining_exposure)

        # If stop loss provided, use risk-based sizing
        if stop_loss_pct and stop_loss_pct > 0:
            risk_amount = equity * self.limits.max_loss_pct
            max_value = min(max_value, risk_amount / stop_loss_pct * price)

        quantity = max_value / price
        return quantity

    def resume_trading(self) -> None:
        """Resume trading after risk pause."""
        self.trading_paused = False
        self.logger.info("Trading resumed")

    def get_risk_status(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Get current risk status."""
        equity = portfolio.equity
        drawdown = 0.0
        if self.initial_equity > 0:
            drawdown = max(0, (self.initial_equity - equity) / self.initial_equity)

        exposure = self._calculate_total_exposure(portfolio)
        exposure_pct = exposure / equity if equity > 0 else 0

        return {
            'trading_paused': self.trading_paused,
            'initial_equity': self.initial_equity,
            'current_equity': equity,
            'drawdown_pct': drawdown,
            'exposure_pct': exposure_pct,
            'cash_reserve_pct': portfolio.cash / equity if equity > 0 else 0,
            'limits': {
                'max_position_size_pct': self.limits.max_position_size_pct,
                'max_total_exposure_pct': self.limits.max_total_exposure_pct,
                'max_loss_pct': self.limits.max_loss_pct,
                'max_drawdown_pct': self.limits.max_drawdown_pct,
                'min_cash_reserve_pct': self.limits.min_cash_reserve_pct
            }
        }

"""
Relative Strength Index (RSI) Indicator
"""

import numpy as np
import pandas as pd
from typing import Union
from .base import Indicator


class RSI(Indicator):
    """
    Relative Strength Index indicator.

    Measures the speed and change of price movements, typically used to identify
    overbought (above 70) or oversold (below 30) conditions.
    """

    def __init__(self, period: int = 14):
        super().__init__(f"RSI_{period}")
        self.period = period

    def calculate(self, data: Union[pd.DataFrame, np.ndarray], **kwargs) -> Union[pd.Series, np.ndarray]:
        """
        Calculate RSI values.

        Args:
            data: OHLCV data
            **kwargs: Additional parameters (period can be overridden)

        Returns:
            RSI values (0-100 scale)
        """
        period = kwargs.get('period', self.period)

        self.validate_data(data)

        if isinstance(data, pd.DataFrame):
            close_prices = data['close']
            delta = close_prices.diff()
        else:
            close_prices = data[:, 3]  # Close price column
            delta = np.diff(close_prices, prepend=close_prices[0])

        # Calculate gains and losses
        gains = np.where(delta > 0, delta, 0)
        losses = np.where(delta < 0, -delta, 0)

        # Calculate average gains and losses
        avg_gains = np.convolve(gains, np.ones(period)/period, mode='valid')
        avg_losses = np.convolve(losses, np.ones(period)/period, mode='valid')

        # Pad to match input length
        avg_gains = np.concatenate([np.full(period-1, np.nan), avg_gains])
        avg_losses = np.concatenate([np.full(period-1, np.nan), avg_losses])

        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        # Handle division by zero
        rsi = np.where(avg_losses == 0, 100, rsi)

        return self.handle_nan(rsi)

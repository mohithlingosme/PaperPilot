"""
Simple Moving Average (SMA) Indicator
"""

import numpy as np
import pandas as pd
from typing import Union
from .base import Indicator


class SMA(Indicator):
    """
    Simple Moving Average indicator.

    Calculates the average price over a specified period.
    """

    def __init__(self, period: int = 20):
        super().__init__(f"SMA_{period}")
        self.period = period

    def calculate(self, data: Union[pd.DataFrame, np.ndarray], **kwargs) -> Union[pd.Series, np.ndarray]:
        """
        Calculate SMA values.

        Args:
            data: OHLCV data
            **kwargs: Additional parameters (period can be overridden)

        Returns:
            SMA values
        """
        period = kwargs.get('period', self.period)

        self.validate_data(data)

        if isinstance(data, pd.DataFrame):
            close_prices = data['close']
            sma = close_prices.rolling(window=period).mean()
        else:
            close_prices = data[:, 3]  # Close price column
            # Calculate rolling mean for numpy array
            sma = np.convolve(close_prices, np.ones(period)/period, mode='valid')
            # Pad to match input length
            sma = np.concatenate([np.full(period-1, np.nan), sma])

        return self.handle_nan(sma)

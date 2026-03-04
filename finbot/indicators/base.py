"""
Base Indicator Class

Provides the common interface and validation for all indicators.
"""

import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import Union, Optional


class Indicator(ABC):
    """
    Abstract base class for all trading indicators.

    Provides common validation and interface methods.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def calculate(self, data: Union[pd.DataFrame, np.ndarray], **kwargs) -> Union[pd.Series, np.ndarray]:
        """
        Calculate the indicator values.

        Args:
            data: OHLCV data as DataFrame or numpy array
            **kwargs: Indicator-specific parameters

        Returns:
            Indicator values as Series or array
        """
        pass

    def validate_data(self, data: Union[pd.DataFrame, np.ndarray]) -> None:
        """
        Validate input data format and content.

        Args:
            data: Input data to validate

        Raises:
            ValueError: If data is invalid
        """
        if isinstance(data, pd.DataFrame):
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in data.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
        elif isinstance(data, np.ndarray):
            if data.ndim != 2 or data.shape[1] < 5:
                raise ValueError("NumPy array must be 2D with at least 5 columns (OHLCV)")
        else:
            raise ValueError("Data must be pandas DataFrame or numpy array")

        if len(data) == 0:
            raise ValueError("Data cannot be empty")

    def handle_nan(self, values: Union[pd.Series, np.ndarray]) -> Union[pd.Series, np.ndarray]:
        """
        Handle NaN values in indicator output.

        Args:
            values: Indicator values

        Returns:
            Values with NaN handling applied
        """
        if isinstance(values, pd.Series):
            return values.fillna(method='bfill').fillna(0)
        else:
            # For numpy arrays, forward fill then fill remaining with 0
            mask = np.isnan(values)
            if np.any(mask):
                # Simple forward fill
                for i in range(1, len(values)):
                    if mask[i]:
                        values[i] = values[i-1] if not mask[i-1] else 0
                # Fill any remaining NaNs at start with 0
                values = np.nan_to_num(values, nan=0)
            return values

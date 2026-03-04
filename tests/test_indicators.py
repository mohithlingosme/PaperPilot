"""
Unit tests for trading indicators.
"""

import numpy as np
import pandas as pd
import pytest
from finbot.indicators import SMA, RSI, Indicator


class TestIndicatorBase:
    """Test the base Indicator class."""

    def test_validation_dataframe_valid(self):
        """Test data validation with valid DataFrame."""
        indicator = Indicator("test")
        data = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [105, 106, 107],
            'low': [95, 96, 97],
            'close': [103, 104, 105],
            'volume': [1000, 1100, 1200]
        })
        # Should not raise
        indicator.validate_data(data)

    def test_validation_dataframe_missing_columns(self):
        """Test data validation with missing columns."""
        indicator = Indicator("test")
        data = pd.DataFrame({
            'open': [100, 101, 102],
            'close': [103, 104, 105]
        })
        with pytest.raises(ValueError, match="Missing required columns"):
            indicator.validate_data(data)

    def test_validation_numpy_valid(self):
        """Test data validation with valid numpy array."""
        indicator = Indicator("test")
        data = np.array([
            [100, 105, 95, 103, 1000],
            [101, 106, 96, 104, 1100],
            [102, 107, 97, 105, 1200]
        ])
        # Should not raise
        indicator.validate_data(data)

    def test_validation_empty_data(self):
        """Test data validation with empty data."""
        indicator = Indicator("test")
        data = pd.DataFrame()
        with pytest.raises(ValueError, match="Data cannot be empty"):
            indicator.validate_data(data)


class TestSMA:
    """Test Simple Moving Average indicator."""

    @pytest.fixture
    def sample_data(self):
        """Sample OHLCV data for testing."""
        return pd.DataFrame({
            'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'high': [105, 106, 107, 108, 109, 110, 111, 112, 113, 114],
            'low': [95, 96, 97, 98, 99, 100, 101, 102, 103, 104],
            'close': [103, 104, 105, 106, 107, 108, 109, 110, 111, 112],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
        })

    def test_calculate_output_shape(self, sample_data):
        """Test that output shape matches input."""
        sma = SMA(period=3)
        result = sma.calculate(sample_data)
        assert len(result) == len(sample_data)

    def test_calculate_deterministic(self, sample_data):
        """Test that results are deterministic."""
        sma = SMA(period=3)
        result1 = sma.calculate(sample_data)
        result2 = sma.calculate(sample_data)
        pd.testing.assert_series_equal(result1, result2)

    def test_calculate_nan_handling(self, sample_data):
        """Test NaN handling for warmup period."""
        sma = SMA(period=5)
        result = sma.calculate(sample_data)
        # First 4 values should be handled (not NaN)
        assert not np.isnan(result.iloc[:4]).any()

    def test_calculate_values(self, sample_data):
        """Test actual SMA calculation."""
        sma = SMA(period=3)
        result = sma.calculate(sample_data)
        # Manual calculation for verification
        expected = sample_data['close'].rolling(window=3).mean()
        pd.testing.assert_series_equal(result, expected.fillna(method='bfill').fillna(0))


class TestRSI:
    """Test Relative Strength Index indicator."""

    @pytest.fixture
    def sample_data(self):
        """Sample OHLCV data for testing."""
        return pd.DataFrame({
            'open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'high': [105, 106, 107, 108, 109, 110, 111, 112, 113, 114],
            'low': [95, 96, 97, 98, 99, 100, 101, 102, 103, 104],
            'close': [103, 104, 105, 106, 107, 108, 109, 110, 111, 112],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
        })

    def test_calculate_output_shape(self, sample_data):
        """Test that output shape matches input."""
        rsi = RSI(period=14)
        result = rsi.calculate(sample_data)
        assert len(result) == len(sample_data)

    def test_calculate_range(self, sample_data):
        """Test that RSI values are in valid range (0-100)."""
        rsi = RSI(period=14)
        result = rsi.calculate(sample_data)
        assert (result >= 0).all() and (result <= 100).all()

    def test_calculate_deterministic(self, sample_data):
        """Test that results are deterministic."""
        rsi = RSI(period=14)
        result1 = rsi.calculate(sample_data)
        result2 = rsi.calculate(sample_data)
        np.testing.assert_array_equal(result1, result2)

    def test_calculate_nan_handling(self, sample_data):
        """Test NaN handling for warmup period."""
        rsi = RSI(period=14)
        result = rsi.calculate(sample_data)
        # Should handle NaN values appropriately
        assert not np.isnan(result).any()

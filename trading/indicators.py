"""
Technical Indicators
Implements common trading indicators using numpy/pandas
"""
import numpy as np
import pandas as pd
from typing import Tuple, Optional


class TechnicalIndicators:
    """Collection of technical analysis indicators"""

    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """
        Exponential Moving Average

        Args:
            data: Price data (typically close prices)
            period: EMA period

        Returns:
            EMA series
        """
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """
        Simple Moving Average

        Args:
            data: Price data
            period: SMA period

        Returns:
            SMA series
        """
        return data.rolling(window=period).mean()

    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Relative Strength Index

        Args:
            data: Price data
            period: RSI period (default 14)

        Returns:
            RSI series (0-100)
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def macd(
        data: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        MACD (Moving Average Convergence Divergence)

        Args:
            data: Price data
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line EMA period

        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        fast_ema = TechnicalIndicators.ema(data, fast_period)
        slow_ema = TechnicalIndicators.ema(data, slow_period)

        macd_line = fast_ema - slow_ema
        signal_line = TechnicalIndicators.ema(macd_line, signal_period)
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    @staticmethod
    def bollinger_bands(
        data: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Bollinger Bands

        Args:
            data: Price data
            period: Moving average period
            std_dev: Number of standard deviations

        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        middle = TechnicalIndicators.sma(data, period)
        std = data.rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return upper, middle, lower

    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Average True Range

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period

        Returns:
            ATR series
        """
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        return atr

    @staticmethod
    def stochastic_oscillator(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14,
        smooth_k: int = 3,
        smooth_d: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Stochastic Oscillator

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Look-back period
            smooth_k: %K smoothing period
            smooth_d: %D smoothing period

        Returns:
            Tuple of (%K, %D)
        """
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()

        k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        k = k.rolling(window=smooth_k).mean()
        d = k.rolling(window=smooth_d).mean()

        return k, d

    @staticmethod
    def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Average Directional Index (Trend Strength)

        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ADX period

        Returns:
            ADX series (0-100, >25 indicates strong trend)
        """
        # Calculate +DM and -DM
        high_diff = high.diff()
        low_diff = -low.diff()

        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

        # Calculate ATR
        atr = TechnicalIndicators.atr(high, low, close, period)

        # Calculate +DI and -DI
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

        # Calculate DX and ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()

        return adx

    @staticmethod
    def support_resistance_levels(
        data: pd.Series,
        window: int = 10,
        threshold: float = 0.02
    ) -> Tuple[list, list]:
        """
        Identify support and resistance levels

        Args:
            data: Price data
            window: Window size for local extrema
            threshold: Minimum distance between levels (as percentage)

        Returns:
            Tuple of (support_levels, resistance_levels)
        """
        # Find local minima (support) and maxima (resistance)
        support = []
        resistance = []

        for i in range(window, len(data) - window):
            # Check if it's a local minimum
            if data.iloc[i] == data.iloc[i - window:i + window + 1].min():
                support.append(data.iloc[i])

            # Check if it's a local maximum
            if data.iloc[i] == data.iloc[i - window:i + window + 1].max():
                resistance.append(data.iloc[i])

        # Remove levels that are too close
        def filter_levels(levels):
            if not levels:
                return []

            levels = sorted(set(levels))
            filtered = [levels[0]]

            for level in levels[1:]:
                if abs(level - filtered[-1]) / filtered[-1] > threshold:
                    filtered.append(level)

            return filtered

        support = filter_levels(support)
        resistance = filter_levels(resistance)

        return support, resistance

    @staticmethod
    def volume_profile(prices: pd.Series, volumes: pd.Series, bins: int = 20) -> pd.DataFrame:
        """
        Calculate volume profile

        Args:
            prices: Price data
            volumes: Volume data
            bins: Number of price bins

        Returns:
            DataFrame with price levels and volume
        """
        # Create price bins
        price_range = prices.max() - prices.min()
        bin_size = price_range / bins

        profile = pd.DataFrame({
            'price': prices,
            'volume': volumes
        })

        profile['bin'] = ((profile['price'] - prices.min()) / bin_size).astype(int)
        profile['bin'] = profile['bin'].clip(0, bins - 1)

        # Aggregate volume by bin
        volume_by_bin = profile.groupby('bin')['volume'].sum()

        return volume_by_bin


class MarketStructure:
    """Analyze market structure and patterns"""

    @staticmethod
    def identify_trend(
        data: pd.Series,
        ema_fast: int = 50,
        ema_slow: int = 200
    ) -> str:
        """
        Identify current trend

        Args:
            data: Price data
            ema_fast: Fast EMA period
            ema_slow: Slow EMA period

        Returns:
            'UPTREND', 'DOWNTREND', or 'SIDEWAYS'
        """
        fast = TechnicalIndicators.ema(data, ema_fast)
        slow = TechnicalIndicators.ema(data, ema_slow)

        if len(data) < ema_slow:
            return 'SIDEWAYS'

        current_fast = fast.iloc[-1]
        current_slow = slow.iloc[-1]
        prev_fast = fast.iloc[-10]
        prev_slow = slow.iloc[-10]

        if current_fast > current_slow and prev_fast > prev_slow:
            return 'UPTREND'
        elif current_fast < current_slow and prev_fast < prev_slow:
            return 'DOWNTREND'
        else:
            return 'SIDEWAYS'

    @staticmethod
    def detect_breakout(
        current_price: float,
        support_levels: list,
        resistance_levels: list,
        threshold: float = 0.001
    ) -> Optional[str]:
        """
        Detect support/resistance breakouts

        Args:
            current_price: Current market price
            support_levels: List of support levels
            resistance_levels: List of resistance levels
            threshold: Breakout threshold (as percentage)

        Returns:
            'SUPPORT_BREAK', 'RESISTANCE_BREAK', or None
        """
        # Check resistance breakout
        for resistance in resistance_levels:
            if current_price > resistance * (1 + threshold):
                return 'RESISTANCE_BREAK'

        # Check support breakout
        for support in support_levels:
            if current_price < support * (1 - threshold):
                return 'SUPPORT_BREAK'

        return None

    @staticmethod
    def higher_highs_higher_lows(high: pd.Series, low: pd.Series, window: int = 5) -> bool:
        """
        Check for higher highs and higher lows (uptrend confirmation)

        Args:
            high: High prices
            low: Low prices
            window: Look-back window

        Returns:
            True if HH and HL pattern detected
        """
        if len(high) < window * 2:
            return False

        recent_high = high.iloc[-window:].max()
        previous_high = high.iloc[-window * 2:-window].max()

        recent_low = low.iloc[-window:].min()
        previous_low = low.iloc[-window * 2:-window].min()

        return recent_high > previous_high and recent_low > previous_low

    @staticmethod
    def lower_highs_lower_lows(high: pd.Series, low: pd.Series, window: int = 5) -> bool:
        """
        Check for lower highs and lower lows (downtrend confirmation)

        Args:
            high: High prices
            low: Low prices
            window: Look-back window

        Returns:
            True if LH and LL pattern detected
        """
        if len(high) < window * 2:
            return False

        recent_high = high.iloc[-window:].max()
        previous_high = high.iloc[-window * 2:-window].max()

        recent_low = low.iloc[-window:].min()
        previous_low = low.iloc[-window * 2:-window].min()

        return recent_high < previous_high and recent_low < previous_low


# Example usage and testing
if __name__ == "__main__":
    # Generate sample data
    np.random.seed(42)
    prices = pd.Series(100 + np.cumsum(np.random.randn(200) * 2))

    # Test indicators
    ind = TechnicalIndicators()

    print("Testing Technical Indicators:")
    print(f"Latest Price: {prices.iloc[-1]:.2f}")
    print(f"EMA(50): {ind.ema(prices, 50).iloc[-1]:.2f}")
    print(f"RSI(14): {ind.rsi(prices, 14).iloc[-1]:.2f}")

    macd, signal, hist = ind.macd(prices)
    print(f"MACD: {macd.iloc[-1]:.4f}")
    print(f"Signal: {signal.iloc[-1]:.4f}")
    print(f"Histogram: {hist.iloc[-1]:.4f}")

    # Test market structure
    ms = MarketStructure()
    trend = ms.identify_trend(prices)
    print(f"\nMarket Trend: {trend}")

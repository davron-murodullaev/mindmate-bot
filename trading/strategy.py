"""
Trading Strategy Implementation
Multi-layer signal confirmation system based on top EA bots
"""
import pandas as pd
import logging
from typing import Optional, Dict, Tuple
from enum import Enum

from trading.indicators import TechnicalIndicators, MarketStructure

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Trade signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class TradingStrategy:
    """
    Advanced trading strategy with 4-layer confirmation

    Inspired by:
    - FX Stabilizer: Multiple timeframe confirmation
    - Flex EA: Adaptive multi-indicator approach
    - Forex Diamond: Trend + Counter-trend logic

    Layer 1: Trend (EMA 50/200)
    Layer 2: Momentum (RSI + MACD)
    Layer 3: Price Action (SMA 20, Price position)
    Layer 4: Volatility (ATR for dynamic stops)
    """

    def __init__(
        self,
        ema_fast: int = 50,
        ema_slow: int = 200,
        sma_short: int = 20,
        rsi_period: int = 14,
        rsi_oversold: int = 30,
        rsi_overbought: int = 70,
        min_confirmations: int = 3
    ):
        """
        Initialize strategy parameters

        Args:
            ema_fast: Fast EMA period
            ema_slow: Slow EMA period
            sma_short: Short SMA period for price action
            rsi_period: RSI calculation period
            rsi_oversold: RSI oversold level
            rsi_overbought: RSI overbought level
            min_confirmations: Minimum confirmations needed (out of 4)
        """
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.sma_short = sma_short
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.min_confirmations = min_confirmations

        self.ind = TechnicalIndicators()
        self.ms = MarketStructure()

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all required indicators

        Args:
            df: DataFrame with OHLC data

        Returns:
            DataFrame with added indicator columns
        """
        # Ensure we have required columns
        required_cols = ['open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # Moving Averages
        df['ema_fast'] = self.ind.ema(df['close'], self.ema_fast)
        df['ema_slow'] = self.ind.ema(df['close'], self.ema_slow)
        df['sma_short'] = self.ind.sma(df['close'], self.sma_short)

        # RSI
        df['rsi'] = self.ind.rsi(df['close'], self.rsi_period)

        # MACD
        macd, signal, hist = self.ind.macd(df['close'])
        df['macd'] = macd
        df['macd_signal'] = signal
        df['macd_hist'] = hist

        # ATR for stop loss calculation
        df['atr'] = self.ind.atr(df['high'], df['low'], df['close'])

        # ADX for trend strength
        df['adx'] = self.ind.adx(df['high'], df['low'], df['close'])

        return df

    def check_layer1_trend(self, df: pd.DataFrame) -> Tuple[int, str]:
        """
        Layer 1: Check trend using EMA crossover

        Returns:
            Tuple of (score, reason)
            1 = bullish, -1 = bearish, 0 = neutral
        """
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        ema_fast_curr = latest['ema_fast']
        ema_slow_curr = latest['ema_slow']
        ema_fast_prev = prev['ema_fast']
        ema_slow_prev = prev['ema_slow']

        # Fresh bullish crossover
        if ema_fast_curr > ema_slow_curr and ema_fast_prev <= ema_slow_prev:
            return 1, "Fresh bullish EMA crossover"

        # Fresh bearish crossover
        if ema_fast_curr < ema_slow_curr and ema_fast_prev >= ema_slow_prev:
            return -1, "Fresh bearish EMA crossover"

        # Established uptrend
        if ema_fast_curr > ema_slow_curr:
            return 1, "Uptrend (EMA 50 > EMA 200)"

        # Established downtrend
        if ema_fast_curr < ema_slow_curr:
            return -1, "Downtrend (EMA 50 < EMA 200)"

        return 0, "No clear trend"

    def check_layer2_momentum(self, df: pd.DataFrame) -> Tuple[int, str]:
        """
        Layer 2: Check momentum using RSI and MACD

        Returns:
            Tuple of (score, reason)
            1 = bullish, -1 = bearish, 0 = neutral
        """
        latest = df.iloc[-1]

        rsi = latest['rsi']
        macd_hist = latest['macd_hist']

        # Strong bullish momentum
        if rsi > 50 and rsi < self.rsi_overbought and macd_hist > 0:
            return 1, f"Bullish momentum (RSI: {rsi:.1f}, MACD+)"

        # Strong bearish momentum
        if rsi < 50 and rsi > self.rsi_oversold and macd_hist < 0:
            return -1, f"Bearish momentum (RSI: {rsi:.1f}, MACD-)"

        # Oversold - potential reversal
        if rsi < self.rsi_oversold and macd_hist > 0:
            return 1, f"Oversold reversal (RSI: {rsi:.1f})"

        # Overbought - potential reversal
        if rsi > self.rsi_overbought and macd_hist < 0:
            return -1, f"Overbought reversal (RSI: {rsi:.1f})"

        return 0, f"Neutral momentum (RSI: {rsi:.1f})"

    def check_layer3_price_action(self, df: pd.DataFrame) -> Tuple[int, str]:
        """
        Layer 3: Check price action relative to SMA

        Returns:
            Tuple of (score, reason)
            1 = bullish, -1 = bearish, 0 = neutral
        """
        latest = df.iloc[-1]

        price = latest['close']
        sma = latest['sma_short']

        # Price above SMA with momentum
        if price > sma * 1.001:  # At least 0.1% above
            return 1, f"Price above SMA20 ({price:.2f} > {sma:.2f})"

        # Price below SMA with momentum
        if price < sma * 0.999:  # At least 0.1% below
            return -1, f"Price below SMA20 ({price:.2f} < {sma:.2f})"

        return 0, "Price near SMA20 (consolidation)"

    def check_layer4_volatility(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Layer 4: Check if volatility is suitable for trading

        Returns:
            Tuple of (is_suitable, reason)
        """
        latest = df.iloc[-1]

        atr = latest['atr']
        price = latest['close']
        adx = latest['adx']

        # Calculate ATR as percentage of price
        atr_pct = (atr / price) * 100

        # Too low volatility (< 0.1%)
        if atr_pct < 0.1:
            return False, f"Volatility too low (ATR: {atr_pct:.3f}%)"

        # Too high volatility (> 5%)
        if atr_pct > 5.0:
            return False, f"Volatility too high (ATR: {atr_pct:.3f}%)"

        # Weak trend (ADX < 20)
        if adx < 20:
            return False, f"Weak trend (ADX: {adx:.1f})"

        return True, f"Good volatility (ATR: {atr_pct:.3f}%, ADX: {adx:.1f})"

    def generate_signal(self, df: pd.DataFrame) -> Dict:
        """
        Generate trading signal based on all layers

        Args:
            df: DataFrame with OHLC data

        Returns:
            Dict with signal info:
            {
                'signal': SignalType,
                'confidence': float (0-1),
                'reasons': list,
                'entry': float,
                'stop_loss': float,
                'take_profit': float
            }
        """
        # Calculate indicators
        df = self.calculate_indicators(df)

        # Check all layers
        trend_score, trend_reason = self.check_layer1_trend(df)
        momentum_score, momentum_reason = self.check_layer2_momentum(df)
        pa_score, pa_reason = self.check_layer3_price_action(df)
        vol_ok, vol_reason = self.check_layer4_volatility(df)

        # Collect reasons and scores
        reasons = [trend_reason, momentum_reason, pa_reason, vol_reason]
        scores = [trend_score, momentum_score, pa_score]

        # Count confirmations
        bullish_confirmations = sum(1 for s in scores if s == 1)
        bearish_confirmations = sum(1 for s in scores if s == -1)

        # Current price and ATR
        latest = df.iloc[-1]
        current_price = latest['close']
        atr = latest['atr']

        # Determine signal
        signal = SignalType.HOLD
        confidence = 0.0

        if vol_ok and bullish_confirmations >= self.min_confirmations:
            signal = SignalType.BUY
            confidence = bullish_confirmations / 4.0

            # Calculate entry, stop loss, and take profit
            entry = current_price
            stop_loss = entry - (2 * atr)
            take_profit = entry + (3 * atr)  # 1:1.5 R:R

        elif vol_ok and bearish_confirmations >= self.min_confirmations:
            signal = SignalType.SELL
            confidence = bearish_confirmations / 4.0

            # Calculate entry, stop loss, and take profit
            entry = current_price
            stop_loss = entry + (2 * atr)
            take_profit = entry - (3 * atr)  # 1:1.5 R:R

        else:
            entry = current_price
            stop_loss = None
            take_profit = None

        # Log signal
        if signal != SignalType.HOLD:
            logger.info(f"🎯 {signal.value} Signal | Confidence: {confidence:.1%}")
            for reason in reasons:
                logger.info(f"   • {reason}")

        return {
            'signal': signal,
            'confidence': confidence,
            'reasons': reasons,
            'entry': entry,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'atr': atr,
            'confirmations': {
                'trend': trend_score,
                'momentum': momentum_score,
                'price_action': pa_score,
                'volatility': vol_ok
            }
        }

    def should_exit(self, df: pd.DataFrame, entry_signal: str, entry_price: float) -> Tuple[bool, str]:
        """
        Check if we should exit current position

        Args:
            df: Current market data
            entry_signal: Original signal ('BUY' or 'SELL')
            entry_price: Entry price

        Returns:
            Tuple of (should_exit, reason)
        """
        # Calculate indicators
        df = self.calculate_indicators(df)

        # Check for opposite signals
        trend_score, trend_reason = self.check_layer1_trend(df)
        momentum_score, momentum_reason = self.check_layer2_momentum(df)

        latest = df.iloc[-1]
        current_price = latest['close']

        # Exit long position
        if entry_signal == 'BUY':
            # Strong bearish signals
            if trend_score == -1 and momentum_score == -1:
                return True, "Strong bearish reversal"

            # Price fell below EMA slow (major support break)
            if current_price < latest['ema_slow']:
                return True, "Price broke below EMA 200"

        # Exit short position
        elif entry_signal == 'SELL':
            # Strong bullish signals
            if trend_score == 1 and momentum_score == 1:
                return True, "Strong bullish reversal"

            # Price rose above EMA slow (major resistance break)
            if current_price > latest['ema_slow']:
                return True, "Price broke above EMA 200"

        return False, "Hold position"


# Example usage and testing
if __name__ == "__main__":
    import numpy as np

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Create sample data
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=300, freq='5min')
    prices = 100 + np.cumsum(np.random.randn(300) * 0.5)

    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices + np.random.randn(300) * 0.1,
        'high': prices + abs(np.random.randn(300) * 0.2),
        'low': prices - abs(np.random.randn(300) * 0.2),
        'close': prices,
    })

    # Initialize strategy
    strategy = TradingStrategy(min_confirmations=3)

    # Generate signal
    signal_info = strategy.generate_signal(df)

    print("\n" + "=" * 50)
    print("SIGNAL ANALYSIS")
    print("=" * 50)
    print(f"Signal: {signal_info['signal'].value}")
    print(f"Confidence: {signal_info['confidence']:.1%}")
    print(f"\nReasons:")
    for reason in signal_info['reasons']:
        print(f"  • {reason}")

    if signal_info['signal'] != SignalType.HOLD:
        print(f"\nEntry: {signal_info['entry']:.2f}")
        print(f"Stop Loss: {signal_info['stop_loss']:.2f}")
        print(f"Take Profit: {signal_info['take_profit']:.2f}")
        risk = abs(signal_info['entry'] - signal_info['stop_loss'])
        reward = abs(signal_info['take_profit'] - signal_info['entry'])
        print(f"R:R Ratio: 1:{reward/risk:.2f}")

"""
Risk Management System
Implements position sizing, risk limits, and trade management
"""
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RiskConfig:
    """Risk management configuration"""
    # Position sizing
    risk_per_trade: float = 0.02  # 2% of balance per trade
    max_position_size: float = 0.10  # Maximum 10% of balance in single trade

    # Loss limits
    max_daily_loss: float = 0.05  # Max 5% daily loss
    max_consecutive_losses: int = 3  # Stop after 3 consecutive losses
    max_drawdown: float = 0.20  # Max 20% total drawdown

    # Trade limits
    max_trades_per_day: int = 10
    min_time_between_trades: int = 300  # 5 minutes in seconds

    # Risk/Reward
    min_risk_reward_ratio: float = 1.5  # Minimum 1:1.5 RR ratio

    # Kelly Criterion
    use_kelly: bool = True
    kelly_fraction: float = 0.5  # Use 50% of Kelly recommendation


@dataclass
class TradeStats:
    """Track trading statistics"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    consecutive_losses: int = 0
    consecutive_wins: int = 0

    total_profit: float = 0.0
    total_loss: float = 0.0

    daily_trades: int = 0
    daily_pnl: float = 0.0
    last_trade_time: Optional[datetime] = None
    last_reset_date: Optional[datetime] = None

    initial_balance: float = 0.0
    peak_balance: float = 0.0
    current_drawdown: float = 0.0

    def reset_daily_stats(self):
        """Reset daily statistics"""
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.last_reset_date = datetime.now().date()
        logger.info("Daily statistics reset")

    def update_drawdown(self, current_balance: float):
        """Update drawdown calculation"""
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance

        if self.peak_balance > 0:
            self.current_drawdown = (self.peak_balance - current_balance) / self.peak_balance

    def record_trade(self, pnl: float, balance: float):
        """Record trade result"""
        self.total_trades += 1
        self.daily_trades += 1
        self.daily_pnl += pnl
        self.last_trade_time = datetime.now()

        if pnl > 0:
            self.winning_trades += 1
            self.total_profit += pnl
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.losing_trades += 1
            self.total_loss += abs(pnl)
            self.consecutive_losses += 1
            self.consecutive_wins = 0

        self.update_drawdown(balance)

    @property
    def win_rate(self) -> float:
        """Calculate win rate"""
        if self.total_trades == 0:
            return 0.0
        return self.winning_trades / self.total_trades

    @property
    def profit_factor(self) -> float:
        """Calculate profit factor"""
        if self.total_loss == 0:
            return float('inf') if self.total_profit > 0 else 0.0
        return self.total_profit / self.total_loss

    @property
    def average_win(self) -> float:
        """Calculate average winning trade"""
        if self.winning_trades == 0:
            return 0.0
        return self.total_profit / self.winning_trades

    @property
    def average_loss(self) -> float:
        """Calculate average losing trade"""
        if self.losing_trades == 0:
            return 0.0
        return self.total_loss / self.losing_trades

    def get_summary(self) -> Dict:
        """Get statistics summary"""
        return {
            'total_trades': self.total_trades,
            'win_rate': f"{self.win_rate * 100:.2f}%",
            'profit_factor': f"{self.profit_factor:.2f}",
            'consecutive_losses': self.consecutive_losses,
            'daily_trades': self.daily_trades,
            'daily_pnl': f"${self.daily_pnl:.2f}",
            'current_drawdown': f"{self.current_drawdown * 100:.2f}%",
            'avg_win': f"${self.average_win:.2f}",
            'avg_loss': f"${self.average_loss:.2f}"
        }


class RiskManager:
    """Comprehensive risk management system"""

    def __init__(self, config: Optional[RiskConfig] = None):
        self.config = config or RiskConfig()
        self.stats = TradeStats()
        self.is_trading_enabled = True

    def initialize(self, initial_balance: float):
        """Initialize with starting balance"""
        self.stats.initial_balance = initial_balance
        self.stats.peak_balance = initial_balance
        self.stats.last_reset_date = datetime.now().date()
        logger.info(f"Risk Manager initialized with balance: ${initial_balance:.2f}")

    def check_daily_reset(self):
        """Check if we need to reset daily stats"""
        today = datetime.now().date()
        if self.stats.last_reset_date != today:
            self.stats.reset_daily_stats()

    def can_trade(self, current_balance: float, reason: str = "") -> tuple[bool, str]:
        """
        Check if we can open a new trade

        Returns:
            Tuple of (can_trade, reason)
        """
        self.check_daily_reset()

        # Check if trading is globally enabled
        if not self.is_trading_enabled:
            return False, "Trading is disabled"

        # Check consecutive losses
        if self.stats.consecutive_losses >= self.config.max_consecutive_losses:
            logger.warning(f"⚠️ Max consecutive losses ({self.config.max_consecutive_losses}) reached")
            return False, f"Max consecutive losses ({self.config.max_consecutive_losses}) reached"

        # Check daily trade limit
        if self.stats.daily_trades >= self.config.max_trades_per_day:
            logger.warning(f"⚠️ Daily trade limit ({self.config.max_trades_per_day}) reached")
            return False, f"Daily trade limit ({self.config.max_trades_per_day}) reached"

        # Check daily loss limit
        daily_loss_pct = abs(self.stats.daily_pnl) / current_balance if current_balance > 0 else 0
        if self.stats.daily_pnl < 0 and daily_loss_pct >= self.config.max_daily_loss:
            logger.warning(f"⚠️ Daily loss limit ({self.config.max_daily_loss * 100}%) reached")
            return False, f"Daily loss limit ({self.config.max_daily_loss * 100:.1f}%) reached"

        # Check total drawdown
        self.stats.update_drawdown(current_balance)
        if self.stats.current_drawdown >= self.config.max_drawdown:
            logger.error(f"🛑 Maximum drawdown ({self.config.max_drawdown * 100}%) exceeded!")
            self.is_trading_enabled = False
            return False, f"Max drawdown ({self.config.max_drawdown * 100:.1f}%) exceeded"

        # Check time between trades
        if self.stats.last_trade_time:
            time_since_last = (datetime.now() - self.stats.last_trade_time).total_seconds()
            if time_since_last < self.config.min_time_between_trades:
                return False, f"Wait {self.config.min_time_between_trades - int(time_since_last)}s before next trade"

        return True, "OK"

    def calculate_position_size(
        self,
        balance: float,
        entry_price: float,
        stop_loss_price: float,
        win_rate: Optional[float] = None
    ) -> float:
        """
        Calculate optimal position size

        Args:
            balance: Account balance
            entry_price: Entry price
            stop_loss_price: Stop loss price
            win_rate: Historical win rate (for Kelly)

        Returns:
            Position size in dollars
        """
        # Calculate risk per trade
        risk_amount = balance * self.config.risk_per_trade

        # Calculate price risk
        price_risk = abs(entry_price - stop_loss_price) / entry_price

        # Basic position size
        position_size = risk_amount

        # Apply Kelly Criterion if enabled and we have sufficient trade history
        if self.config.use_kelly and self.stats.total_trades >= 20:
            win_rate = win_rate or self.stats.win_rate
            avg_win = self.stats.average_win
            avg_loss = self.stats.average_loss

            if avg_loss > 0 and win_rate > 0:
                # Kelly formula: f = (p*b - q) / b
                # where p = win rate, q = loss rate, b = win/loss ratio
                b = avg_win / avg_loss
                kelly = (win_rate * b - (1 - win_rate)) / b

                # Use fraction of Kelly (typically 0.25 to 0.5)
                kelly = max(0, kelly) * self.config.kelly_fraction

                # Apply Kelly to position size
                kelly_position = balance * kelly
                position_size = min(risk_amount, kelly_position)

                logger.info(f"Kelly position size: ${kelly_position:.2f} (Kelly: {kelly:.2%})")

        # Ensure position size doesn't exceed maximum
        max_position = balance * self.config.max_position_size
        position_size = min(position_size, max_position)

        logger.info(f"Position size: ${position_size:.2f} (Risk: ${risk_amount:.2f})")
        return round(position_size, 2)

    def validate_trade_setup(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float
    ) -> tuple[bool, str]:
        """
        Validate trade setup parameters

        Returns:
            Tuple of (is_valid, reason)
        """
        # Calculate risk/reward ratio
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)

        if risk == 0:
            return False, "Invalid stop loss (no risk)"

        rr_ratio = reward / risk

        if rr_ratio < self.config.min_risk_reward_ratio:
            logger.warning(f"⚠️ Poor R:R ratio: 1:{rr_ratio:.2f} (min: 1:{self.config.min_risk_reward_ratio})")
            return False, f"R:R ratio too low: 1:{rr_ratio:.2f}"

        logger.info(f"✓ Trade setup valid | R:R = 1:{rr_ratio:.2f}")
        return True, f"1:{rr_ratio:.2f}"

    def record_trade_result(self, pnl: float, balance: float):
        """
        Record trade result and update statistics

        Args:
            pnl: Profit/loss of the trade
            balance: Current account balance
        """
        self.stats.record_trade(pnl, balance)

        result = "WIN" if pnl > 0 else "LOSS"
        logger.info(f"{'✓' if pnl > 0 else '✗'} Trade {result}: ${pnl:+.2f} | Balance: ${balance:.2f}")

        # Log statistics periodically
        if self.stats.total_trades % 10 == 0:
            self.print_statistics()

    def print_statistics(self):
        """Print current statistics"""
        stats = self.stats.get_summary()
        logger.info("=" * 50)
        logger.info("TRADING STATISTICS")
        logger.info("=" * 50)
        for key, value in stats.items():
            logger.info(f"{key.replace('_', ' ').title()}: {value}")
        logger.info("=" * 50)

    def get_stats(self) -> TradeStats:
        """Get current statistics"""
        return self.stats

    def enable_trading(self):
        """Enable trading"""
        self.is_trading_enabled = True
        logger.info("✓ Trading enabled")

    def disable_trading(self):
        """Disable trading"""
        self.is_trading_enabled = False
        logger.warning("⚠️ Trading disabled")

    def reset_stats(self, keep_history: bool = False):
        """Reset statistics"""
        if keep_history:
            # Keep total stats, reset daily only
            self.stats.reset_daily_stats()
        else:
            # Full reset
            self.stats = TradeStats()
            self.stats.initial_balance = self.stats.peak_balance

        logger.info("Statistics reset")


# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Initialize risk manager
    config = RiskConfig(
        risk_per_trade=0.02,
        max_daily_loss=0.05,
        max_consecutive_losses=3
    )

    rm = RiskManager(config)
    rm.initialize(initial_balance=1000.0)

    # Simulate some trades
    balance = 1000.0

    # Trade 1: Win
    can_trade, reason = rm.can_trade(balance)
    if can_trade:
        position_size = rm.calculate_position_size(balance, 100, 98)
        pnl = 20
        balance += pnl
        rm.record_trade_result(pnl, balance)

    # Trade 2: Loss
    can_trade, reason = rm.can_trade(balance)
    if can_trade:
        position_size = rm.calculate_position_size(balance, 100, 98)
        pnl = -20
        balance += pnl
        rm.record_trade_result(pnl, balance)

    # Print final stats
    rm.print_statistics()

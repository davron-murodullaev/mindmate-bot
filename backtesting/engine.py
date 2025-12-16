"""
Backtesting Engine
Test trading strategies on historical data
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path

from trading.strategy import TradingStrategy, SignalType
from trading.risk_manager import RiskManager, RiskConfig

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Backtest trading strategies on historical data

    Features:
    - Realistic trade simulation
    - Commission and slippage modeling
    - Detailed performance metrics
    - Trade-by-trade analysis
    """

    def __init__(
        self,
        initial_balance: float = 1000.0,
        commission: float = 0.0,  # Deriv has no commission for most products
        slippage: float = 0.0001,  # 0.01% slippage
        risk_config: Optional[RiskConfig] = None
    ):
        """
        Initialize backtesting engine

        Args:
            initial_balance: Starting balance
            commission: Commission per trade (as percentage)
            slippage: Price slippage (as percentage)
            risk_config: Risk management configuration
        """
        self.initial_balance = initial_balance
        self.commission = commission
        self.slippage = slippage

        # Initialize components
        self.strategy = TradingStrategy()
        self.risk_manager = RiskManager(risk_config or RiskConfig())
        self.risk_manager.initialize(initial_balance)

        # State
        self.balance = initial_balance
        self.equity = initial_balance
        self.trades: List[Dict] = []
        self.equity_curve: List[Dict] = []

    def run(self, data: pd.DataFrame, show_progress: bool = True) -> Dict:
        """
        Run backtest on historical data

        Args:
            data: DataFrame with OHLC data
            show_progress: Show progress during backtest

        Returns:
            Backtest results dictionary
        """
        logger.info("=" * 60)
        logger.info("STARTING BACKTEST")
        logger.info("=" * 60)
        logger.info(f"Initial Balance: ${self.initial_balance:.2f}")
        logger.info(f"Data Points: {len(data)}")
        logger.info(f"Date Range: {data['timestamp'].iloc[0]} to {data['timestamp'].iloc[-1]}")
        logger.info("=" * 60 + "\n")

        open_position = None
        total_bars = len(data)

        # Iterate through each candle
        for i in range(200, total_bars):  # Start after sufficient history
            current_data = data.iloc[:i+1].copy()
            current_bar = data.iloc[i]

            # Update equity curve
            self.equity_curve.append({
                'timestamp': current_bar['timestamp'],
                'equity': self.balance,
                'drawdown': self.risk_manager.stats.current_drawdown
            })

            # Show progress
            if show_progress and i % 100 == 0:
                progress = (i / total_bars) * 100
                logger.info(f"Progress: {progress:.1f}% | Balance: ${self.balance:.2f} | Trades: {len(self.trades)}")

            # If we have an open position, check for exit
            if open_position:
                exit_price = current_bar['close']
                should_exit = False
                exit_reason = ""

                # Check stop loss
                if open_position['signal'] == 'BUY':
                    if current_bar['low'] <= open_position['stop_loss']:
                        should_exit = True
                        exit_price = open_position['stop_loss']
                        exit_reason = "Stop Loss"

                    # Check take profit
                    elif current_bar['high'] >= open_position['take_profit']:
                        should_exit = True
                        exit_price = open_position['take_profit']
                        exit_reason = "Take Profit"

                else:  # SELL
                    if current_bar['high'] >= open_position['stop_loss']:
                        should_exit = True
                        exit_price = open_position['stop_loss']
                        exit_reason = "Stop Loss"

                    elif current_bar['low'] <= open_position['take_profit']:
                        should_exit = True
                        exit_price = open_position['take_profit']
                        exit_reason = "Take Profit"

                # Check strategy exit signal
                if not should_exit:
                    should_strategy_exit, strategy_reason = self.strategy.should_exit(
                        current_data,
                        open_position['signal'],
                        open_position['entry_price']
                    )
                    if should_strategy_exit:
                        should_exit = True
                        exit_reason = f"Strategy: {strategy_reason}"

                # Execute exit
                if should_exit:
                    # Apply slippage
                    if open_position['signal'] == 'BUY':
                        exit_price *= (1 - self.slippage)
                    else:
                        exit_price *= (1 + self.slippage)

                    # Calculate P&L
                    if open_position['signal'] == 'BUY':
                        pnl = (exit_price - open_position['entry_price']) / open_position['entry_price']
                    else:
                        pnl = (open_position['entry_price'] - exit_price) / open_position['entry_price']

                    pnl_dollars = pnl * open_position['position_size']

                    # Apply commission
                    pnl_dollars -= (open_position['position_size'] * self.commission * 2)  # Entry + exit

                    # Update balance
                    self.balance += pnl_dollars

                    # Record trade
                    trade_record = {
                        'entry_time': open_position['entry_time'],
                        'exit_time': current_bar['timestamp'],
                        'signal': open_position['signal'],
                        'entry_price': open_position['entry_price'],
                        'exit_price': exit_price,
                        'stop_loss': open_position['stop_loss'],
                        'take_profit': open_position['take_profit'],
                        'position_size': open_position['position_size'],
                        'pnl': pnl_dollars,
                        'pnl_pct': pnl * 100,
                        'exit_reason': exit_reason,
                        'balance': self.balance
                    }

                    self.trades.append(trade_record)
                    self.risk_manager.record_trade_result(pnl_dollars, self.balance)

                    # Log trade
                    result_emoji = "✓" if pnl_dollars > 0 else "✗"
                    logger.info(f"{result_emoji} Trade #{len(self.trades)} | {open_position['signal']} | P&L: ${pnl_dollars:+.2f} ({pnl*100:+.2f}%) | Reason: {exit_reason}")

                    # Clear position
                    open_position = None

            # If no position, look for entry signal
            else:
                # Check if we can trade
                can_trade, reason = self.risk_manager.can_trade(self.balance)
                if not can_trade:
                    continue

                # Generate signal
                signal_info = self.strategy.generate_signal(current_data)

                if signal_info['signal'] != SignalType.HOLD:
                    # Validate trade setup
                    is_valid, _ = self.risk_manager.validate_trade_setup(
                        signal_info['entry'],
                        signal_info['stop_loss'],
                        signal_info['take_profit']
                    )

                    if not is_valid:
                        continue

                    # Calculate position size
                    position_size = self.risk_manager.calculate_position_size(
                        self.balance,
                        signal_info['entry'],
                        signal_info['stop_loss']
                    )

                    if position_size == 0:
                        continue

                    # Apply slippage to entry
                    entry_price = signal_info['entry']
                    if signal_info['signal'] == SignalType.BUY:
                        entry_price *= (1 + self.slippage)
                    else:
                        entry_price *= (1 - self.slippage)

                    # Open position
                    open_position = {
                        'signal': signal_info['signal'].value,
                        'entry_time': current_bar['timestamp'],
                        'entry_price': entry_price,
                        'stop_loss': signal_info['stop_loss'],
                        'take_profit': signal_info['take_profit'],
                        'position_size': position_size
                    }

                    logger.info(f"\n📈 Opened {signal_info['signal'].value} position")
                    logger.info(f"   Entry: {entry_price:.4f}")
                    logger.info(f"   Stop Loss: {signal_info['stop_loss']:.4f}")
                    logger.info(f"   Take Profit: {signal_info['take_profit']:.4f}")
                    logger.info(f"   Size: ${position_size:.2f}\n")

        # Close any remaining position at last price
        if open_position:
            logger.info("⚠️ Closing position at end of backtest")
            exit_price = data.iloc[-1]['close']

            if open_position['signal'] == 'BUY':
                pnl = (exit_price - open_position['entry_price']) / open_position['entry_price']
            else:
                pnl = (open_position['entry_price'] - exit_price) / open_position['entry_price']

            pnl_dollars = pnl * open_position['position_size']
            self.balance += pnl_dollars

            self.trades.append({
                'entry_time': open_position['entry_time'],
                'exit_time': data.iloc[-1]['timestamp'],
                'signal': open_position['signal'],
                'entry_price': open_position['entry_price'],
                'exit_price': exit_price,
                'pnl': pnl_dollars,
                'exit_reason': 'End of backtest',
                'balance': self.balance
            })

        # Calculate results
        results = self.calculate_results()

        # Print results
        self.print_results(results)

        return results

    def calculate_results(self) -> Dict:
        """Calculate performance metrics"""
        if not self.trades:
            return {
                'error': 'No trades executed'
            }

        trades_df = pd.DataFrame(self.trades)

        # Basic metrics
        total_trades = len(self.trades)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        # P&L metrics
        total_pnl = self.balance - self.initial_balance
        total_pnl_pct = (total_pnl / self.initial_balance) * 100

        gross_profit = trades_df[trades_df['pnl'] > 0]['pnl'].sum() if winning_trades > 0 else 0
        gross_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum()) if losing_trades > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        # Average metrics
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = abs(trades_df[trades_df['pnl'] < 0]['pnl'].mean()) if losing_trades > 0 else 0

        # Drawdown
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['peak'] - equity_df['equity']) / equity_df['peak']
        max_drawdown = equity_df['drawdown'].max()

        # Sharpe ratio (simplified)
        returns = trades_df['pnl_pct'] if 'pnl_pct' in trades_df.columns else trades_df['pnl'] / self.initial_balance * 100
        sharpe_ratio = returns.mean() / returns.std() if returns.std() > 0 else 0

        # Trade duration (if timestamps available)
        if 'entry_time' in trades_df.columns and 'exit_time' in trades_df.columns:
            trades_df['duration'] = pd.to_datetime(trades_df['exit_time']) - pd.to_datetime(trades_df['entry_time'])
            avg_duration = trades_df['duration'].mean()
        else:
            avg_duration = None

        return {
            'initial_balance': self.initial_balance,
            'final_balance': self.balance,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'avg_duration': avg_duration,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }

    def print_results(self, results: Dict):
        """Print backtest results"""
        logger.info("\n" + "=" * 60)
        logger.info("BACKTEST RESULTS")
        logger.info("=" * 60)

        logger.info(f"Initial Balance:    ${results['initial_balance']:.2f}")
        logger.info(f"Final Balance:      ${results['final_balance']:.2f}")
        logger.info(f"Total P&L:          ${results['total_pnl']:+.2f} ({results['total_pnl_pct']:+.2f}%)")
        logger.info("=" * 60)

        logger.info(f"Total Trades:       {results['total_trades']}")
        logger.info(f"Winning Trades:     {results['winning_trades']}")
        logger.info(f"Losing Trades:      {results['losing_trades']}")
        logger.info(f"Win Rate:           {results['win_rate']*100:.2f}%")
        logger.info("=" * 60)

        logger.info(f"Gross Profit:       ${results['gross_profit']:.2f}")
        logger.info(f"Gross Loss:         ${results['gross_loss']:.2f}")
        logger.info(f"Profit Factor:      {results['profit_factor']:.2f}")
        logger.info(f"Avg Win:            ${results['avg_win']:.2f}")
        logger.info(f"Avg Loss:           ${results['avg_loss']:.2f}")
        logger.info("=" * 60)

        logger.info(f"Max Drawdown:       {results['max_drawdown']*100:.2f}%")
        logger.info(f"Sharpe Ratio:       {results['sharpe_ratio']:.2f}")

        if results['avg_duration']:
            logger.info(f"Avg Trade Duration: {results['avg_duration']}")

        logger.info("=" * 60)

        # Performance rating
        rating = self.rate_performance(results)
        logger.info(f"Performance Rating: {rating}")
        logger.info("=" * 60 + "\n")

    def rate_performance(self, results: Dict) -> str:
        """Rate the performance of the strategy"""
        score = 0

        # Win rate (max 25 points)
        if results['win_rate'] >= 0.60:
            score += 25
        elif results['win_rate'] >= 0.50:
            score += 20
        elif results['win_rate'] >= 0.40:
            score += 10

        # Profit factor (max 25 points)
        if results['profit_factor'] >= 2.0:
            score += 25
        elif results['profit_factor'] >= 1.5:
            score += 20
        elif results['profit_factor'] >= 1.2:
            score += 10

        # Return (max 25 points)
        if results['total_pnl_pct'] >= 50:
            score += 25
        elif results['total_pnl_pct'] >= 30:
            score += 20
        elif results['total_pnl_pct'] >= 10:
            score += 10

        # Max drawdown (max 25 points)
        if results['max_drawdown'] <= 0.10:
            score += 25
        elif results['max_drawdown'] <= 0.20:
            score += 20
        elif results['max_drawdown'] <= 0.30:
            score += 10

        # Rating
        if score >= 80:
            return "⭐⭐⭐⭐⭐ EXCELLENT"
        elif score >= 60:
            return "⭐⭐⭐⭐ GOOD"
        elif score >= 40:
            return "⭐⭐⭐ AVERAGE"
        elif score >= 20:
            return "⭐⭐ POOR"
        else:
            return "⭐ VERY POOR"

    def save_results(self, filename: str = None):
        """Save results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backtest_results_{timestamp}.json"

        results = self.calculate_results()

        # Convert timestamps to strings
        for trade in results['trades']:
            if 'entry_time' in trade:
                trade['entry_time'] = str(trade['entry_time'])
            if 'exit_time' in trade:
                trade['exit_time'] = str(trade['exit_time'])

        for point in results['equity_curve']:
            point['timestamp'] = str(point['timestamp'])

        # Save
        output_dir = Path("logs")
        output_dir.mkdir(exist_ok=True)
        filepath = output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"✓ Results saved to {filepath}")


# Example usage
if __name__ == "__main__":
    import asyncio
    from trading.deriv_api import DerivAPI

    async def run_backtest():
        # Setup logging
        logging.basicConfig(level=logging.INFO)

        # Load historical data
        api = DerivAPI()
        await api.connect()

        candles = await api.get_ticks_history(
            symbol="R_100",
            count=5000,
            style="candles",
            granularity=300
        )

        await api.disconnect()

        # Convert to DataFrame
        df = pd.DataFrame(candles)
        for col in ['open', 'high', 'low', 'close']:
            df[col] = pd.to_numeric(df[col])
        df['epoch'] = pd.to_numeric(df['epoch'])
        df['timestamp'] = pd.to_datetime(df['epoch'], unit='s')

        # Run backtest
        engine = BacktestEngine(initial_balance=1000.0)
        results = engine.run(df)

        # Save results
        engine.save_results()

    # Run
    asyncio.run(run_backtest())

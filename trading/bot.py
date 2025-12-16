"""
TradeMate Trading Bot
Main bot implementation combining all components
"""
import asyncio
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict
import json
from pathlib import Path

from trading.deriv_api import DerivAPI
from trading.strategy import TradingStrategy, SignalType
from trading.risk_manager import RiskManager, RiskConfig
from trading.indicators import TechnicalIndicators

logger = logging.getLogger(__name__)


class TradeMateBot:
    """
    Advanced Deriv Trading Bot

    Features:
    - Multi-layer signal confirmation
    - Advanced risk management
    - Real-time market monitoring
    - Automated trade execution
    - Performance tracking
    """

    def __init__(
        self,
        api_token: str,
        symbol: str = "R_100",
        initial_stake: float = 10.0,
        candle_interval: int = 300,  # 5 minutes
        risk_config: Optional[RiskConfig] = None,
        demo_mode: bool = True
    ):
        """
        Initialize TradeMate Bot

        Args:
            api_token: Deriv API token
            symbol: Trading symbol (e.g., 'R_100', 'R_75', 'frxEURUSD')
            initial_stake: Initial stake per trade
            candle_interval: Candle interval in seconds (60, 300, 900, etc.)
            risk_config: Risk management configuration
            demo_mode: Use demo account (recommended for testing)
        """
        self.api = DerivAPI()
        self.api_token = api_token
        self.symbol = symbol
        self.initial_stake = initial_stake
        self.candle_interval = candle_interval
        self.demo_mode = demo_mode

        # Initialize components
        self.strategy = TradingStrategy(min_confirmations=3)
        self.risk_manager = RiskManager(risk_config or RiskConfig())

        # State
        self.is_running = False
        self.current_position: Optional[Dict] = None
        self.balance = 0.0
        self.start_time = None

        # Data storage
        self.market_data = pd.DataFrame()
        self.trade_log = []

        # Logs directory
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)

    async def connect(self):
        """Connect to Deriv API and initialize"""
        try:
            logger.info("🚀 Starting TradeMate Bot...")

            # Connect to Deriv
            await self.api.connect()

            # Authorize
            await self.api.authorize(self.api_token)

            # Get account balance
            self.balance = await self.api.get_balance()

            # Initialize risk manager
            self.risk_manager.initialize(self.balance)

            # Get account info
            account_info = await self.api.get_account_info()
            account_type = "DEMO" if self.demo_mode else "REAL"

            logger.info("=" * 60)
            logger.info(f"✓ Connected to Deriv ({account_type} Account)")
            logger.info(f"  Balance: ${self.balance:.2f}")
            logger.info(f"  Symbol: {self.symbol}")
            logger.info(f"  Candle Interval: {self.candle_interval}s")
            logger.info(f"  Initial Stake: ${self.initial_stake}")
            logger.info("=" * 60)

            self.start_time = datetime.now()
            return True

        except Exception as e:
            logger.error(f"✗ Connection failed: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Deriv API"""
        await self.api.disconnect()
        logger.info("Disconnected from Deriv")

    async def load_market_data(self, count: int = 300) -> pd.DataFrame:
        """
        Load historical market data

        Args:
            count: Number of candles to load (max 5000)

        Returns:
            DataFrame with OHLC data
        """
        try:
            candles = await self.api.get_ticks_history(
                symbol=self.symbol,
                count=count,
                style="candles",
                granularity=self.candle_interval
            )

            # Convert to DataFrame
            df = pd.DataFrame(candles)

            # Convert numeric columns
            for col in ['open', 'high', 'low', 'close']:
                df[col] = pd.to_numeric(df[col])

            df['epoch'] = pd.to_numeric(df['epoch'])
            df['timestamp'] = pd.to_datetime(df['epoch'], unit='s')

            logger.info(f"✓ Loaded {len(df)} candles")
            return df

        except Exception as e:
            logger.error(f"✗ Failed to load market data: {e}")
            raise

    async def analyze_market(self) -> Dict:
        """
        Analyze current market and generate signal

        Returns:
            Signal information dict
        """
        # Load latest market data
        df = await self.load_market_data(count=300)

        # Store market data
        self.market_data = df

        # Generate signal
        signal_info = self.strategy.generate_signal(df)

        return signal_info

    async def execute_trade(self, signal_info: Dict) -> bool:
        """
        Execute trade based on signal

        Args:
            signal_info: Signal information from strategy

        Returns:
            True if trade executed successfully
        """
        signal = signal_info['signal']

        if signal == SignalType.HOLD:
            return False

        # Check if we can trade
        can_trade, reason = self.risk_manager.can_trade(self.balance)
        if not can_trade:
            logger.warning(f"⚠️ Cannot trade: {reason}")
            return False

        # Validate trade setup
        is_valid, rr_reason = self.risk_manager.validate_trade_setup(
            signal_info['entry'],
            signal_info['stop_loss'],
            signal_info['take_profit']
        )

        if not is_valid:
            logger.warning(f"⚠️ Invalid trade setup: {rr_reason}")
            return False

        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            self.balance,
            signal_info['entry'],
            signal_info['stop_loss']
        )

        if position_size == 0:
            logger.warning("⚠️ Position size is zero, skipping trade")
            return False

        # Place trade
        try:
            contract_type = "CALL" if signal == SignalType.BUY else "PUT"

            logger.info(f"📈 Placing {signal.value} trade...")
            logger.info(f"   Entry: {signal_info['entry']:.4f}")
            logger.info(f"   Stop Loss: {signal_info['stop_loss']:.4f}")
            logger.info(f"   Take Profit: {signal_info['take_profit']:.4f}")
            logger.info(f"   Position Size: ${position_size:.2f}")

            # For Deriv, we'll use a simple duration-based contract
            # You can modify this for other contract types (Multipliers, etc.)
            duration = 10  # 10 ticks or adjust as needed

            contract = await self.api.buy_contract(
                contract_type=contract_type,
                symbol=self.symbol,
                amount=position_size,
                duration=duration,
                duration_unit="t"  # ticks
            )

            # Store position
            self.current_position = {
                'contract_id': contract.get('contract_id'),
                'signal': signal.value,
                'entry_price': signal_info['entry'],
                'stop_loss': signal_info['stop_loss'],
                'take_profit': signal_info['take_profit'],
                'position_size': position_size,
                'entry_time': datetime.now(),
                'reasons': signal_info['reasons']
            }

            logger.info(f"✓ Trade executed | Contract ID: {contract.get('contract_id')}")
            return True

        except Exception as e:
            logger.error(f"✗ Failed to execute trade: {e}")
            return False

    async def monitor_position(self):
        """Monitor open position and manage exits"""
        if not self.current_position:
            return

        try:
            contract_id = self.current_position['contract_id']

            # Get contract details
            details = await self.api.get_contract_details(contract_id)

            # Check if contract is still open
            if details.get('is_sold'):
                # Contract closed
                pnl = float(details.get('profit', 0))
                sell_price = float(details.get('sell_price', 0))

                logger.info(f"{'✓' if pnl > 0 else '✗'} Position closed | P&L: ${pnl:+.2f}")

                # Update balance
                self.balance = await self.api.get_balance()

                # Record trade
                self.risk_manager.record_trade_result(pnl, self.balance)

                # Log trade
                self.trade_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'signal': self.current_position['signal'],
                    'entry': self.current_position['entry_price'],
                    'exit': sell_price,
                    'pnl': pnl,
                    'balance': self.balance
                })

                # Clear position
                self.current_position = None

        except Exception as e:
            logger.error(f"✗ Error monitoring position: {e}")

    async def trading_loop(self):
        """Main trading loop"""
        logger.info("\n🤖 Trading loop started")
        logger.info("Monitoring market for signals...\n")

        check_interval = 60  # Check every minute

        while self.is_running:
            try:
                # Monitor existing position
                if self.current_position:
                    await self.monitor_position()
                    await asyncio.sleep(10)  # Check position more frequently
                    continue

                # Analyze market for new opportunities
                signal_info = await self.analyze_market()

                # Execute trade if signal present
                if signal_info['signal'] != SignalType.HOLD:
                    await self.execute_trade(signal_info)

                # Wait before next check
                logger.info(f"Waiting {check_interval}s before next check... | Balance: ${self.balance:.2f}")
                await asyncio.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("\n⚠️ Stopping bot...")
                break
            except Exception as e:
                logger.error(f"✗ Error in trading loop: {e}")
                await asyncio.sleep(check_interval)

    async def start(self):
        """Start the trading bot"""
        try:
            # Connect
            await self.connect()

            # Set running flag
            self.is_running = True

            # Start trading loop
            await self.trading_loop()

        except KeyboardInterrupt:
            logger.info("\n⚠️ Bot stopped by user")
        except Exception as e:
            logger.error(f"✗ Fatal error: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """Stop the trading bot"""
        self.is_running = False

        # Close any open positions
        if self.current_position:
            logger.info("Closing open position...")
            # Implement position closing logic here

        # Save trade log
        self.save_trade_log()

        # Print final statistics
        self.risk_manager.print_statistics()

        # Calculate session statistics
        if self.start_time:
            runtime = datetime.now() - self.start_time
            logger.info(f"\n{'='*60}")
            logger.info(f"SESSION SUMMARY")
            logger.info(f"{'='*60}")
            logger.info(f"Runtime: {runtime}")
            logger.info(f"Starting Balance: ${self.risk_manager.stats.initial_balance:.2f}")
            logger.info(f"Final Balance: ${self.balance:.2f}")
            profit = self.balance - self.risk_manager.stats.initial_balance
            profit_pct = (profit / self.risk_manager.stats.initial_balance) * 100 if self.risk_manager.stats.initial_balance > 0 else 0
            logger.info(f"Total P&L: ${profit:+.2f} ({profit_pct:+.2f}%)")
            logger.info(f"{'='*60}")

        # Disconnect
        await self.disconnect()

        logger.info("✓ Bot stopped successfully")

    def save_trade_log(self):
        """Save trade log to file"""
        if not self.trade_log:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"trades_{timestamp}.json"

        with open(log_file, 'w') as f:
            json.dump(self.trade_log, f, indent=2)

        logger.info(f"✓ Trade log saved to {log_file}")


# Command-line interface
async def main():
    """Main entry point for command-line usage"""
    import argparse
    import os
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Parse arguments
    parser = argparse.ArgumentParser(description="TradeMate - Advanced Deriv Trading Bot")
    parser.add_argument('--token', type=str, help='Deriv API token')
    parser.add_argument('--symbol', type=str, default='R_100', help='Trading symbol (default: R_100)')
    parser.add_argument('--stake', type=float, default=10.0, help='Initial stake per trade (default: 10.0)')
    parser.add_argument('--interval', type=int, default=300, help='Candle interval in seconds (default: 300)')
    parser.add_argument('--demo', action='store_true', default=True, help='Use demo account (default: True)')
    parser.add_argument('--real', action='store_true', help='Use real account (WARNING: real money!)')

    args = parser.parse_args()

    # Get API token
    api_token = args.token or os.getenv('DERIV_API_TOKEN')

    if not api_token:
        print("❌ Error: No API token provided!")
        print("   Use --token argument or set DERIV_API_TOKEN environment variable")
        return

    # Determine account type
    demo_mode = not args.real

    if not demo_mode:
        print("\n" + "⚠️ " * 20)
        print("WARNING: You are about to use a REAL ACCOUNT with REAL MONEY!")
        print("Are you sure you want to continue? (yes/no)")
        print("⚠️ " * 20 + "\n")

        confirmation = input("> ").strip().lower()
        if confirmation != 'yes':
            print("Aborted.")
            return

    # Create bot
    bot = TradeMateBot(
        api_token=api_token,
        symbol=args.symbol,
        initial_stake=args.stake,
        candle_interval=args.interval,
        demo_mode=demo_mode
    )

    # Start bot
    await bot.start()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Run bot
    asyncio.run(main())

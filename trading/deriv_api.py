"""
Deriv API Wrapper
Handles all communication with Deriv.com API
"""
import asyncio
import json
import logging
from typing import Optional, Dict, List, Any
import websockets
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DerivAPI:
    """Async Deriv API wrapper"""

    def __init__(self, app_id: str = "1089", endpoint: str = "wss://ws.derivws.com/websockets/v3"):
        self.app_id = app_id
        self.endpoint = f"{endpoint}?app_id={app_id}"
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.authorized = False
        self.api_token: Optional[str] = None
        self._request_id = 0

    def _get_request_id(self) -> int:
        """Generate unique request ID"""
        self._request_id += 1
        return self._request_id

    async def connect(self):
        """Connect to Deriv WebSocket"""
        try:
            self.ws = await websockets.connect(self.endpoint)
            logger.info("✓ Connected to Deriv API")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to Deriv: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Deriv WebSocket"""
        if self.ws:
            await self.ws.close()
            logger.info("Disconnected from Deriv API")

    async def send_request(self, request: Dict) -> Dict:
        """Send request and wait for response"""
        if not self.ws:
            raise Exception("Not connected to Deriv API")

        request['req_id'] = self._get_request_id()
        await self.ws.send(json.dumps(request))

        # Wait for response with matching req_id
        while True:
            response = json.loads(await self.ws.recv())
            if response.get('req_id') == request['req_id']:
                if 'error' in response:
                    logger.error(f"API Error: {response['error']}")
                    raise Exception(f"API Error: {response['error']['message']}")
                return response

    async def authorize(self, api_token: str) -> Dict:
        """Authorize with API token"""
        self.api_token = api_token
        response = await self.send_request({"authorize": api_token})

        if 'authorize' in response:
            self.authorized = True
            logger.info(f"✓ Authorized: {response['authorize']['email']}")
            return response['authorize']
        else:
            raise Exception("Authorization failed")

    async def get_balance(self) -> float:
        """Get account balance"""
        if not self.authorized:
            raise Exception("Not authorized")

        response = await self.send_request({"balance": 1, "subscribe": 0})
        balance = float(response['balance']['balance'])
        logger.info(f"Balance: ${balance:.2f}")
        return balance

    async def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.authorized:
            raise Exception("Not authorized")

        response = await self.send_request({"get_settings": 1})
        return response.get('get_settings', {})

    async def get_ticks_history(
        self,
        symbol: str,
        count: int = 5000,
        end: str = "latest",
        style: str = "candles",
        granularity: int = 60
    ) -> List[Dict]:
        """
        Get historical ticks/candles

        Args:
            symbol: Market symbol (e.g., 'R_100', 'frxEURUSD')
            count: Number of ticks (max 5000)
            end: End time ('latest' or epoch)
            style: 'ticks' or 'candles'
            granularity: Candle size in seconds (60, 120, 180, 300, 600, 900, 1800, 3600, 7200, 14400, 28800, 86400)
        """
        request = {
            "ticks_history": symbol,
            "count": count,
            "end": end,
            "style": style,
        }

        if style == "candles":
            request["granularity"] = granularity

        response = await self.send_request(request)

        if style == "candles":
            candles = response.get('candles', [])
            logger.info(f"✓ Loaded {len(candles)} candles for {symbol}")
            return candles
        else:
            history = response.get('history', {})
            ticks = []
            if 'times' in history and 'prices' in history:
                for time, price in zip(history['times'], history['prices']):
                    ticks.append({'epoch': time, 'quote': price})
            logger.info(f"✓ Loaded {len(ticks)} ticks for {symbol}")
            return ticks

    async def get_active_symbols(self, landing_company: str = "svg") -> List[Dict]:
        """Get list of available symbols"""
        response = await self.send_request({
            "active_symbols": "brief",
            "product_type": "basic",
            "landing_company": landing_company
        })

        symbols = response.get('active_symbols', [])
        logger.info(f"✓ Loaded {len(symbols)} active symbols")
        return symbols

    async def buy_contract(
        self,
        contract_type: str,
        symbol: str,
        amount: float,
        duration: int,
        duration_unit: str = "t",
        barrier: Optional[str] = None,
        basis: str = "stake"
    ) -> Dict:
        """
        Buy a contract

        Args:
            contract_type: 'CALL', 'PUT', 'MULTUP', 'MULTDOWN', etc.
            symbol: Market symbol
            amount: Stake amount
            duration: Contract duration
            duration_unit: 't' (ticks), 'm' (minutes), 'h' (hours), 'd' (days)
            barrier: Barrier level (for barrier contracts)
            basis: 'stake' or 'payout'
        """
        if not self.authorized:
            raise Exception("Not authorized")

        request = {
            "buy": 1,
            "price": amount,
            "parameters": {
                "contract_type": contract_type,
                "symbol": symbol,
                "amount": amount,
                "duration": duration,
                "duration_unit": duration_unit,
                "basis": basis
            }
        }

        if barrier:
            request["parameters"]["barrier"] = barrier

        response = await self.send_request(request)
        contract = response.get('buy', {})

        logger.info(f"✓ Contract opened: {contract_type} {symbol} | ${amount} | ID: {contract.get('contract_id')}")
        return contract

    async def sell_contract(self, contract_id: int, price: float) -> Dict:
        """Sell an open contract"""
        if not self.authorized:
            raise Exception("Not authorized")

        response = await self.send_request({
            "sell": contract_id,
            "price": price
        })

        sell_info = response.get('sell', {})
        logger.info(f"✓ Contract sold: ID {contract_id} | Sold at ${sell_info.get('sold_for', 0)}")
        return sell_info

    async def get_open_contracts(self) -> List[Dict]:
        """Get all open contracts"""
        if not self.authorized:
            raise Exception("Not authorized")

        response = await self.send_request({"portfolio": 1})
        contracts = response.get('portfolio', {}).get('contracts', [])

        logger.info(f"Open contracts: {len(contracts)}")
        return contracts

    async def get_contract_details(self, contract_id: int) -> Dict:
        """Get details of a specific contract"""
        response = await self.send_request({"proposal_open_contract": 1, "contract_id": contract_id})
        return response.get('proposal_open_contract', {})

    async def get_proposal(
        self,
        contract_type: str,
        symbol: str,
        amount: float,
        duration: int,
        duration_unit: str = "t",
        basis: str = "stake"
    ) -> Dict:
        """
        Get contract proposal (price quote)
        """
        request = {
            "proposal": 1,
            "contract_type": contract_type,
            "symbol": symbol,
            "amount": amount,
            "duration": duration,
            "duration_unit": duration_unit,
            "basis": basis
        }

        response = await self.send_request(request)
        return response.get('proposal', {})

    async def subscribe_ticks(self, symbol: str, callback):
        """
        Subscribe to live tick stream

        Args:
            symbol: Market symbol
            callback: Async function to handle tick data
        """
        await self.send_request({"ticks": symbol, "subscribe": 1})

        logger.info(f"✓ Subscribed to {symbol} ticks")

        # Listen for tick updates
        try:
            while True:
                message = json.loads(await self.ws.recv())
                if 'tick' in message:
                    await callback(message['tick'])
        except Exception as e:
            logger.error(f"Tick subscription error: {e}")

    async def subscribe_candles(self, symbol: str, granularity: int, callback):
        """
        Subscribe to live candle stream

        Args:
            symbol: Market symbol
            granularity: Candle size in seconds
            callback: Async function to handle candle data
        """
        await self.send_request({
            "ticks_history": symbol,
            "style": "candles",
            "granularity": granularity,
            "count": 1,
            "end": "latest",
            "subscribe": 1
        })

        logger.info(f"✓ Subscribed to {symbol} {granularity}s candles")

        # Listen for candle updates
        try:
            while True:
                message = json.loads(await self.ws.recv())
                if 'ohlc' in message:
                    await callback(message['ohlc'])
        except Exception as e:
            logger.error(f"Candle subscription error: {e}")


# Convenience functions
async def test_connection():
    """Test Deriv API connection"""
    api = DerivAPI()
    try:
        await api.connect()

        # Get active symbols
        symbols = await api.get_active_symbols()
        print(f"✓ Found {len(symbols)} active symbols")

        # Get some tick history
        ticks = await api.get_ticks_history("R_100", count=10, style="ticks")
        print(f"✓ Latest R_100 price: {ticks[-1]['quote']}")

        await api.disconnect()
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the API
    asyncio.run(test_connection())

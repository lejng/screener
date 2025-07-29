from dataclasses import dataclass
from enum import Enum
from ccxt.base.types import Ticker

from src.config.custom_logger import CustomLogger

logger = CustomLogger()

class MarketType(Enum):
    SPOT = ('spot')
    SWAP = ('swap')
    UNKNOWN = ('unknown')

    def __init__(self, type_name: str):
        self.exchange_name: str = type_name

class ExchangeName(Enum):
    BYBIT = ('BYBIT')
    MEXC = ('MEXC')
    GATE = ('GATEIO'),
    KRAKEN = ('KRAKEN')

    def __init__(self, exchange_name: str):
        self.exchange_name: str = exchange_name

@dataclass
class TickerData:
    exchange_id: str
    symbol: str
    base_currency: str
    quote_currency: str
    mark_price: float
    last_price: float
    bid: float
    ask: float
    exchange: ExchangeName
    market_type: MarketType

    def get_trading_view_name(self) -> str:
        if self.market_type is MarketType.SPOT:
            return f"{self.exchange.exchange_name}:{self.base_currency}{self.quote_currency}"
        if self.market_type is MarketType.SWAP:
            return f"{self.exchange.exchange_name}:{self.base_currency}{self.quote_currency}.P"
        return f"{self.exchange.exchange_name}:{self.base_currency}{self.quote_currency}.UNKNOWN"

def parse_symbol(symbol: str, exchange: ExchangeName) -> tuple[str, str]:
    try:
        if symbol == 'MX_USDT':
            return 'MX', 'USDT'
        parts = symbol.replace(':', '/').split('/')
        return parts[0], parts[1]
    except (AttributeError, IndexError):
        logger.log_info(f"Error symbol format: {symbol}, exchange: {exchange}")
        return 'UNKNOWN', 'UNKNOWN'

def convert_ticker(tickers: dict[str, Ticker], exchange: ExchangeName, market_type: MarketType) -> dict[str, list[TickerData]]:
    tickers_grouped_by_base_currency = {}
    for key, item in tickers.items():
        base, quote = parse_symbol(item.get('symbol', ''), exchange)
        if base not in tickers_grouped_by_base_currency:
            tickers_grouped_by_base_currency[base] = []
        tickers_grouped_by_base_currency[base].append(
            TickerData(
                exchange_id=key,
                symbol=item['symbol'],  # "BTC/USDT:USDT"
                base_currency=base,
                quote_currency=quote,
                mark_price=item['markPrice'],
                last_price=item['last'],
                bid=item['bid'],
                ask=item['ask'],
                exchange=exchange,
                market_type=market_type
            )
        )

    return tickers_grouped_by_base_currency
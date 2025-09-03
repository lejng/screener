from dataclasses import dataclass

from src.connectors.data.ticker_info import TickerInfo


@dataclass
class SpreadData:
    ticker_to_buy: TickerInfo
    ticker_to_sell: TickerInfo
    spread_percent: float
    base_currency: str
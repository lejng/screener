from dataclasses import dataclass

from src.connectors.data.base_ticker_info import BaseTickerInfo


@dataclass
class SpreadData:
    ticker_to_buy: BaseTickerInfo
    ticker_to_sell: BaseTickerInfo
    spread_percent: float
    base_currency: str
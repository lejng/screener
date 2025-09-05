from dataclasses import dataclass

from src.connectors.data.base_ticker_info import BaseTickerInfo


@dataclass
class SpreadData:
    ticker_to_buy: BaseTickerInfo
    ticker_to_sell: BaseTickerInfo
    spread_percent: float
    base_currency: str

    def get_funding_spread_adjustment(self) -> float:
        add_to_spread: float = 0
        to_buy_rate = self.ticker_to_buy.get_funding_info()
        to_sell_rate = self.ticker_to_sell.get_funding_info()
        if to_buy_rate:
            add_to_spread -= to_buy_rate.get_funding_rate_percent()
        if to_sell_rate:
            add_to_spread += to_sell_rate.get_funding_rate_percent()
        return add_to_spread
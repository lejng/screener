from dataclasses import dataclass
from typing import List, Tuple

from ccxt.base.types import OrderBook, Num

from src.connectors.data.ticker_info import TickerInfo


@dataclass
class AggregateTicker:
    ticker: TickerInfo
    order_book: OrderBook

    def vwap(self, asks_or_bids: List[List[Num]], amount_in_quote: float) -> float | None:
        # level[0] - price, level[1] - volume
        levels = [(level[0], level[1]) for level in asks_or_bids if level[1] > 0]
        remaining_in_currency = amount_in_quote
        bought_amount = 0.0

        for price, volume in levels:
            take_volume = min(volume, remaining_in_currency / price)
            spent = take_volume * price
            bought_amount += take_volume
            remaining_in_currency -= spent
            if remaining_in_currency <= 0:
                break

        if remaining_in_currency > 0:
            return None

        avg_price = amount_in_quote / bought_amount
        return avg_price

    # amount it mean in usd or usdt or different quote currency
    def vwap_order_book(self, amount_in_quote) -> Tuple[float, float]:
        vwap_buy = self.vwap(self.order_book["asks"], amount_in_quote)
        vwap_sell = self.vwap(self.order_book["bids"], amount_in_quote)
        return vwap_buy, vwap_sell
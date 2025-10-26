from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from ccxt.base.types import OrderBook, Num

from src.connectors.data.base_ticker_info import BaseTickerInfo
from src.connectors.data.funding_rate_info import FundingRateInfo

@dataclass
class FullTickerInfo(BaseTickerInfo):
    order_book: OrderBook
    funding_rate_info: Optional[FundingRateInfo]
    amount_in_quote: float

    _best_buy_price: Optional[float] = field(default=None, init=False, repr=False)
    _best_sell_price: Optional[float] = field(default=None, init=False, repr=False)

    # amount it mean in usd or usdt or different quote currency
    @classmethod
    def create(cls, ticker_info: BaseTickerInfo, order_book: OrderBook, amount_in_quote: float,
               funding_rate_info: Optional[FundingRateInfo] = None) -> FullTickerInfo:
        return cls(
            ticker_info.ticker,
            ticker_info.exchange_name,
            ticker_info.spot,
            ticker_info.swap,
            ticker_info.future,
            ticker_info.base_currency,
            ticker_info.quote_currency,
            order_book,
            funding_rate_info,
            amount_in_quote
        )

    def get_amount_in_quote(self) -> Optional[float]:
        return self.amount_in_quote

    def get_best_buy_price(self) -> Optional[float]:
        if self._best_buy_price is None:
            self._best_buy_price = self.vwap(self.order_book["asks"])
        return self._best_buy_price

    def get_best_sell_price(self) -> Optional[float]:
        if self._best_sell_price is None:
            self._best_sell_price = self.vwap(self.order_book["bids"])
        return self._best_sell_price

    def get_coins_to_buy(self) -> Optional[float]:
        price = self.get_best_buy_price()
        if price is None or price == 0:
            return None
        return self.amount_in_quote / price

    def get_coins_to_sell(self) -> Optional[float]:
        price = self.get_best_sell_price()
        if price is None or price == 0:
            return None
        return self.amount_in_quote / price

    def get_funding_info(self) -> Optional[FundingRateInfo]:
        return self.funding_rate_info

    def vwap(self, asks_or_bids: List[List[Num]], shift: float = 1.2) -> float | None:
        # level[0] - price, level[1] - volume
        levels = [(level[0], level[1]) for level in asks_or_bids if level[1] > 0]
        # used shift as 20% by default
        amount_in_quote_adjusted_shift = shift * self.amount_in_quote
        remaining_in_currency = amount_in_quote_adjusted_shift
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

        avg_price = amount_in_quote_adjusted_shift / bought_amount
        return avg_price
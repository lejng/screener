from dataclasses import dataclass
from typing import Optional

from src.config.custom_logger import CustomLogger
from src.connectors.common_connector import TickerInfo


@dataclass
class SpreadData:
    ticker_to_buy: TickerInfo
    ticker_to_sell: TickerInfo
    spread_percent: float
    base_currency: str

def convert_to_spread_data(ticker_to_buy: TickerInfo, ticker_to_sell: TickerInfo, spread: float, base_currency: str) -> SpreadData:
    return SpreadData(
        ticker_to_buy=ticker_to_buy,
        ticker_to_sell=ticker_to_sell,
        spread_percent=spread,
        base_currency=base_currency
    )

class ArbitrageFounder:
    def __init__(self):
        self.logger = CustomLogger()

    def find_arbitrage(self, tickers: dict[str, list[TickerInfo]], min_spread=1) -> list[SpreadData]:
        spread_list_result = []
        for base_currency, value in tickers.items():
            spread_list_result.extend(self.calculate_spreads(value, min_spread, base_currency))
        return sorted(spread_list_result, key=lambda x: x.spread_percent, reverse=True)

    def calculate_spreads(self, tickers: list[TickerInfo], min_spread: float, base_currency: str) -> list[SpreadData]:
        result: list[SpreadData] = []
        size = len(tickers)

        for i in range(size):
            ticker_1 = tickers[i]

            for j in range(i + 1, size):
                ticker_2 = tickers[j]
                spread_data = self.calculate_spread(ticker_1, ticker_2, min_spread, base_currency)
                if spread_data is not None:
                    result.append(spread_data)

        return result

    def calculate_spread(self, ticker_1: TickerInfo, ticker_2: TickerInfo, min_spread: float, base_currency: str) -> Optional[SpreadData]:
        spreads: list[SpreadData] = []
        if None in (ticker_1.get_ask(), ticker_1.get_bid()):
            self.logger.log_info(f"{ticker_1.get_symbol()} on {ticker_1.exchange_name} has bid or ask price None")
        if None in (ticker_2.get_ask(), ticker_2.get_bid()):
            self.logger.log_info(f"{ticker_2.get_symbol()} on {ticker_2.exchange_name} has bid or ask price None")
        spread_1 = self.calculate_spread_bid_ask(ticker_1, ticker_2, min_spread, base_currency)
        if spread_1 is not None:
            spreads.append(spread_1)
        spread_2 = self.calculate_spread_bid_ask(ticker_2, ticker_1, min_spread, base_currency)
        if spread_2 is not None:
            spreads.append(spread_2)
        if not spreads:
            if None in (ticker_1.get_ask(), ticker_2.get_bid()) or None in (ticker_2.get_ask(), ticker_1.get_bid()):
                spreads = self.calculate_spread_last_price(ticker_1, ticker_2, min_spread, base_currency)
        if not spreads:
            return None
        return max(spreads, key=lambda x: x.spread_percent)

    def calculate_spread_bid_ask(self, ticker_1: TickerInfo, ticker_2: TickerInfo, min_spread: float, base_currency: str) -> Optional[SpreadData]:
        # ask - I buy ask price
        # bid - I sell bid price
        buy_price_1 = ticker_1.get_ask()
        sell_price_2 = ticker_2.get_bid()
        if None not in (buy_price_1, sell_price_2) and buy_price_1 < sell_price_2:
            spread_percent = self.calculate_buy_sell_spread_percent(buy_price_1, sell_price_2)
            if spread_percent > min_spread:
                return convert_to_spread_data(ticker_1, ticker_2, spread_percent, base_currency)
        return None

    def calculate_spread_last_price(self, ticker_1: TickerInfo, ticker_2: TickerInfo, min_spread: float, base_currency: str) -> list[SpreadData]:
        spreads: list[SpreadData] = []
        if ticker_1.get_last_price() is None:
            self.logger.log_info(f"{ticker_1.get_symbol()} on {ticker_1.exchange_name} has last price None")
        if ticker_2.get_last_price() is None:
            self.logger.log_info(f"{ticker_2.get_symbol()} on {ticker_2.exchange_name} has last price None")
        if None not in (ticker_1.get_last_price(), ticker_2.get_last_price()):
            if ticker_1.get_last_price() < ticker_2.get_last_price():
                spread_percent = self.calculate_buy_sell_spread_percent(ticker_1.get_last_price(), ticker_2.get_last_price())
                if spread_percent > min_spread:
                    spreads.append(convert_to_spread_data(ticker_1, ticker_2, spread_percent, base_currency))
            if ticker_2.get_last_price() < ticker_1.get_last_price():
                spread_percent = self.calculate_buy_sell_spread_percent(ticker_2.get_last_price(), ticker_1.get_last_price())
                if spread_percent > min_spread:
                    spreads.append(convert_to_spread_data(ticker_2, ticker_1, spread_percent, base_currency))
        return spreads

    def calculate_buy_sell_spread_percent(self, buy: float, sell: float):
        if buy <= 0 or sell <= 0:
            return 0
            # if sell <= buy:
            #    return 0
        try:
            spread_percent = ((sell - buy) / buy) * 100
            return spread_percent
        except TypeError:
            self.logger.log_error(f"Error during spread calculation")
            return 0

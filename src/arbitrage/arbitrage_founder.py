from typing import Optional

from src.arbitrage.data.spread_data import SpreadData
from src.config.custom_logger import CustomLogger
from src.connectors.data.base_ticker_info import BaseTickerInfo

def convert_to_spread_data(ticker_to_buy: BaseTickerInfo, ticker_to_sell: BaseTickerInfo, spread: float, base_currency: str) -> SpreadData:
    return SpreadData(
        ticker_to_buy=ticker_to_buy,
        ticker_to_sell=ticker_to_sell,
        spread_percent=spread,
        base_currency=base_currency
    )

class ArbitrageFounder:
    def __init__(self):
        self.logger = CustomLogger()

    def find_arbitrage(self, tickers_per_base_currency: dict[str, list[BaseTickerInfo]], min_spread=1) -> list[SpreadData]:
        spread_list_result = []
        for base_currency, tickers in tickers_per_base_currency.items():
            spread_list_result.extend(self.calculate_spreads(tickers, min_spread, base_currency))
        spreads: list[SpreadData] = sorted(spread_list_result, key=lambda x: x.spread_percent, reverse=True)
        filtered_spreads = [
            item for item in spreads
            if item.ticker_to_sell.get_best_sell_price() > item.ticker_to_buy.get_best_buy_price()
        ]
        return filtered_spreads

    def calculate_spreads(self, tickers: list[BaseTickerInfo], min_spread: float, base_currency: str) -> list[SpreadData]:
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

    def calculate_spread(self, ticker_1: BaseTickerInfo, ticker_2: BaseTickerInfo, min_spread: float, base_currency: str) -> Optional[SpreadData]:

        if None in (ticker_1.get_best_buy_price(), ticker_1.get_best_sell_price()):
            self.logger.log_info(f"{ticker_1.get_symbol()} on {ticker_1.exchange_name} has bid or ask price None")
        if None in (ticker_2.get_best_buy_price(), ticker_2.get_best_sell_price()):
            self.logger.log_info(f"{ticker_2.get_symbol()} on {ticker_2.exchange_name} has bid or ask price None")
        spread_1 = self.calculate_spread_bid_ask(ticker_1, ticker_2, min_spread, base_currency)
        spread_2 = self.calculate_spread_bid_ask(ticker_2, ticker_1, min_spread, base_currency)
        valid_spreads = [spread for spread in (spread_1, spread_2) if spread is not None]
        return max(valid_spreads, key=lambda x: x.spread_percent, default=None)

    def calculate_spread_bid_ask(self, ticker_1: BaseTickerInfo, ticker_2: BaseTickerInfo, min_spread: float, base_currency: str) -> Optional[SpreadData]:
        buy_price_1 = ticker_1.get_best_buy_price()
        sell_price_2 = ticker_2.get_best_sell_price()
        if None not in (buy_price_1, sell_price_2) and buy_price_1 < sell_price_2:
            spread_percent = self.calculate_buy_sell_spread_percent(buy_price_1, sell_price_2)
            if spread_percent > min_spread:
                return convert_to_spread_data(ticker_1, ticker_2, spread_percent, base_currency)
        return None

    def calculate_buy_sell_spread_percent(self, buy: float, sell: float):
        if buy <= 0 or sell <= 0:
            return 0
            # if sell <= buy:
            #    return 0
        try:
            spread_percent = ((sell - buy) / buy) * 100
            return spread_percent
        except Exception as e:
            self.logger.log_error(f"Error during spread calculation: {e}")
            return 0

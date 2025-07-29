from typing import Optional

from src.arbitrage.common import calculate_buy_sell_spread_percent, SpreadData
from src.config.custom_logger import CustomLogger
from src.connectors.common import ExchangeName, TickerData
from src.connectors.rest_spot_common_connector import RestSpotCommonConnector
from src.connectors.rest_swap_common_connector import RestSwapCommonConnector
from concurrent.futures import ThreadPoolExecutor, as_completed

class ArbitrageFounder:
    def __init__(self, allowed_quotes: set[str], exclude_base: set[str]):
        self.rest_swap_connector = RestSwapCommonConnector(allowed_quotes, exclude_base)
        self.rest_spot_connector = RestSpotCommonConnector(allowed_quotes, exclude_base)
        self.logger = CustomLogger()

    def update_allowed_quotes(self, allowed_quotes: set[str]):
        self.rest_swap_connector.allowed_quotes = allowed_quotes
        self.rest_spot_connector.allowed_quotes = allowed_quotes

    def update_exclude_base(self, exclude_base: set[str]):
        self.rest_swap_connector.exclude_base = exclude_base
        self.rest_spot_connector.exclude_base = exclude_base

    def fetch_spot_tickers(self, spot_exchanges: list[ExchangeName])  -> dict[str, list[TickerData]]:
        tickers = {}
        for name in spot_exchanges:
            current_tickers = self.rest_spot_connector.fetch_spot_by_exchange(name)
            tickers = self.merge_tickers(tickers, current_tickers)
        return tickers

    def fetch_swap_tickers(self, swap_exchanges: list[ExchangeName])  -> dict[str, list[TickerData]]:
        tickers = {}
        for name in swap_exchanges:
            current_tickers = self.rest_swap_connector.fetch_swap_by_exchange(name)
            tickers = self.merge_tickers(tickers, current_tickers)
        return tickers

    def fetch_tickers_in_parallel(self, swap_exchanges: list[ExchangeName], spot_exchanges: list[ExchangeName]) -> dict[str, list[TickerData]]:
        tickers = {}
        max_workers = len(spot_exchanges) + len(swap_exchanges)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for name in spot_exchanges:
                future = executor.submit(self.rest_spot_connector.fetch_spot_by_exchange, name)
                futures[future] = name

            for name in swap_exchanges:
                future = executor.submit(self.rest_swap_connector.fetch_swap_by_exchange, name)
                futures[future] = name

            for future in as_completed(futures):
                try:
                    current_tickers = future.result()
                    tickers = self.merge_tickers(tickers, current_tickers)
                except Exception as e:
                    self.logger.log_error(f"Error fetching data from {futures[future]}: {e}")

        return tickers

    @staticmethod
    def merge_tickers(*ticker_dicts: dict[str, list[TickerData]]) -> dict[str, list[TickerData]]:
        merged = {}

        for ticker_dict in ticker_dicts:
            for symbol, tickers in ticker_dict.items():
                if symbol not in merged:
                    merged[symbol] = []
                merged[symbol].extend(tickers)

        return merged

    def find_arbitrage(self, swap_exchanges: list[ExchangeName], spot_exchanges: list[ExchangeName], min_spread=0.7) -> list[SpreadData]:
        # how to do it in parallel???
        """
        tickers: dict[str, list[TickerData]] = self.merge_tickers(
            self.fetch_swap_tickers(swap_exchanges),
            self.fetch_spot_tickers(spot_exchanges)
        )
        """
        tickers: dict[str, list[TickerData]] = self.fetch_tickers_in_parallel(swap_exchanges, spot_exchanges)
        spread_list_result = []
        for base_currency, value in tickers.items():
            spread_list_result.extend(self.calculate_spreads(value, min_spread, base_currency))
        return sorted(spread_list_result, key=lambda x: x.spread_percent, reverse=True)


    def calculate_spreads(self, tickers: list[TickerData], min_spread: float, base_currency: str) -> list[SpreadData]:
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

    def calculate_spread(self, ticker_1: TickerData, ticker_2: TickerData, min_spread: float, base_currency: str) -> Optional[SpreadData]:
        # ask - I buy ask price
        # bid - I sell bid price
        buy_price_1 = ticker_1.ask
        sell_price_1 = ticker_1.bid
        buy_price_2 = ticker_2.ask
        sell_price_2 = ticker_2.bid
        spreads: list[SpreadData] = []
        if  None not in (buy_price_1, sell_price_2) and buy_price_1 < sell_price_2:
            spread_percent = calculate_buy_sell_spread_percent(buy_price_1, sell_price_2)
            if spread_percent > min_spread:
                spreads.append(self.convert_to_spread_data(ticker_1, ticker_2, spread_percent, base_currency))
        if None not in (buy_price_2, sell_price_1) and buy_price_2 < sell_price_1:
            spread_percent = calculate_buy_sell_spread_percent(buy_price_2, sell_price_1)
            if spread_percent > min_spread:
                spreads.append(self.convert_to_spread_data(ticker_2, ticker_1, spread_percent, base_currency))
        if not spreads:
            return None
        return max(spreads, key=lambda x: x.spread_percent)

    def convert_to_spread_data(self, ticker_to_buy: TickerData, ticker_to_sell: TickerData, spread: float, base_currency: str) -> SpreadData:
        return SpreadData(
            ticker_to_buy=ticker_to_buy,
            ticker_to_sell=ticker_to_sell,
            spread_percent=spread,
            base_currency=base_currency
        )

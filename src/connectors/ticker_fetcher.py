from concurrent.futures import ThreadPoolExecutor, as_completed

from ccxt.base.types import OrderBook

from src.config.custom_logger import CustomLogger
from src.connectors.common_connector import CommonConnector
from src.connectors.data.aggregate_ticker import AggregateTicker
from src.connectors.data.ticker_info import TickerInfo

class TickerFetcher:

    def __init__(self):
        self.logger = CustomLogger()

    def fetch_tickers_by_base(self, connectors: list[CommonConnector], base: str) -> list[AggregateTicker]:
        self.logger.log_info(f"Fetching ticker by base {base}")
        result: list[AggregateTicker] = []
        for connector in connectors:
            spot_symbols = connector.load_spot_symbols_by_base(base)
            for symbol in spot_symbols:
                ticker: TickerInfo = connector.fetch_spot_ticker(symbol)
                order_book: OrderBook = connector.fetch_spot_order_book(symbol)
                result.append(AggregateTicker(ticker, order_book))
            swap_symbols = connector.load_swap_symbols_by_base(base)
            for symbol in swap_symbols:
                ticker: TickerInfo = connector.fetch_swap_ticker(symbol)
                order_book: OrderBook = connector.fetch_swap_order_book(symbol)
                result.append(AggregateTicker(ticker, order_book))
        return result

    def fetch_tickers_in_parallel(self, spot_connectors: list[CommonConnector],
                                  swap_connectors: list[CommonConnector],
                                  futures_connectors: list[CommonConnector]) -> dict[str, list[TickerInfo]]:
        tickers = {}
        max_workers = 20

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for connector in spot_connectors:
                futures.append(executor.submit(connector.fetch_spot_tickers))

            for connector in swap_connectors:
                futures.append(executor.submit(connector.fetch_swap_tickers))

            for connector in futures_connectors:
                futures.append(executor.submit(connector.fetch_future_tickers))

            for future in as_completed(futures):
                try:
                    current_tickers = future.result()
                    tickers = self.merge_tickers(tickers, current_tickers)
                except Exception as e:
                    self.logger.log_error(f"Error fetching data from: {e}")

        return tickers

    @staticmethod
    def merge_tickers(ticker_dict: dict[str, list[TickerInfo]], tickers: list[TickerInfo]) -> dict[str, list[TickerInfo]]:
        for ticker in tickers:
            key = ticker.base_currency
            if key in ticker_dict:
                ticker_dict[key].append(ticker)
            else:
                ticker_dict[key] = [ticker]
        return ticker_dict
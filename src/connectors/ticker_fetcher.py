from concurrent.futures import ThreadPoolExecutor, as_completed

from ccxt.base.types import OrderBook

from src.config.custom_logger import CustomLogger
from src.connectors.common_connector import CommonConnector
from src.connectors.data.full_ticker_info import FullTickerInfo
from src.connectors.data.base_ticker_info import BaseTickerInfo
from src.connectors.data.funding_rate_info import FundingRateInfo


class TickerFetcher:

    def __init__(self):
        self.logger = CustomLogger()

    def fetch_tickers_by_base(self, spot_connectors: list[CommonConnector],
                              swap_connectors: list[CommonConnector],
                              futures_connectors: list[CommonConnector],
                              base: str,
                              amount_in_quote: float) -> list[FullTickerInfo]:
        self.logger.log_info(f"Fetching ticker by base {base}")
        result: list[FullTickerInfo] = []
        for connector in spot_connectors:
            symbols = connector.load_spot_symbols_by_base(base)
            for symbol in symbols:
                ticker: BaseTickerInfo = connector.fetch_spot_ticker(symbol)
                order_book: OrderBook = connector.fetch_spot_order_book(symbol)
                result.append(FullTickerInfo.create(ticker, order_book, amount_in_quote))
        for connector in swap_connectors:
            symbols = connector.load_swap_symbols_by_base(base)
            for symbol in symbols:
                ticker: BaseTickerInfo = connector.fetch_swap_ticker(symbol)
                order_book: OrderBook = connector.fetch_swap_order_book(symbol)
                funding_rate_info: FundingRateInfo = connector.fetch_funding_rate(symbol)
                result.append(FullTickerInfo.create(ticker, order_book, amount_in_quote,  funding_rate_info))
        for connector in futures_connectors:
            symbols = connector.load_futures_symbols_by_base(base)
            for symbol in symbols:
                ticker: BaseTickerInfo = connector.fetch_future_ticker(symbol)
                order_book: OrderBook = connector.fetch_future_order_book(symbol)
                result.append(FullTickerInfo.create(ticker, order_book, amount_in_quote))
        return result

    def fetch_tickers_in_parallel(self, spot_connectors: list[CommonConnector],
                                  swap_connectors: list[CommonConnector],
                                  futures_connectors: list[CommonConnector]) -> dict[str, list[BaseTickerInfo]]:
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
    def merge_tickers(ticker_dict: dict[str, list[BaseTickerInfo]], tickers: list[BaseTickerInfo]) -> dict[str, list[BaseTickerInfo]]:
        for ticker in tickers:
            key = ticker.base_currency
            if key in ticker_dict:
                ticker_dict[key].append(ticker)
            else:
                ticker_dict[key] = [ticker]
        return ticker_dict
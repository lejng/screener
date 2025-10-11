from src.arbitrage.arbitrage_founder import ArbitrageFounder
from src.arbitrage.data.spread_data import SpreadData
from src.arbitrage.data.supported_exchanges import SupportedExchanges
from src.connectors.common_connector import CommonConnector
from src.connectors.data.base_ticker_info import BaseTickerInfo
from src.connectors.data.full_ticker_info import FullTickerInfo
from src.connectors.data.funding_rate_info import FundingRateInfo
from src.connectors.future.future_common_connector import FutureCommonConnector
from src.connectors.spot.spot_common_connector import SpotCommonConnector
from src.connectors.swap.swap_common_connector import SwapCommonConnector
from src.connectors.ticker_fetcher import TickerFetcher


# ============= Utils methods =============
# remove situation where buy futures/swap and sell spot, because usually impossible open short spot position
def filter_wrong_pairs(spreads: list[SpreadData]) -> list[SpreadData]:
     return [
        item for item in spreads
        if not (item.ticker_to_sell.spot
                and (item.ticker_to_buy.swap or item.ticker_to_buy.future))
    ]
class ArbitrageFacade:

    def __init__(self, all_spot_connectors: list[SpotCommonConnector],
                 all_swap_connectors: list[SwapCommonConnector],
                 all_futures_connectors: list[FutureCommonConnector]):
        self.ticker_fetcher = TickerFetcher()
        self.founder = ArbitrageFounder()
        self.all_spot_connectors: list[SpotCommonConnector] = all_spot_connectors
        self.all_swap_connectors: list[SwapCommonConnector] = all_swap_connectors
        self.all_futures_connectors: list[FutureCommonConnector] = all_futures_connectors

    def get_full_ticker_info_for_swap_coin(self, base: str, amount_in_quote: float, exchanges: list[str]) -> list[FullTickerInfo]:
        tickers: list[FullTickerInfo] = self.ticker_fetcher.fetch_tickers_by_base(
            [],
            self.get_swap_connectors(exchanges),
            [],
            base,
            amount_in_quote
        )
        return tickers

    def get_top_funding_rates(self, exchange: str) -> dict[str, list[FundingRateInfo]]:
        for connector in self.all_swap_connectors:
            if connector.get_exchange_name() == exchange:
                return connector.fetch_top_funding_rates()
        return {'max': [], 'small': []}

    def find_all_spreads(self, min_spread: float, max_spread: float,
                     exchanges: SupportedExchanges) -> list[SpreadData]:
        spreads: list[SpreadData] = self.find_spreads(min_spread, max_spread, exchanges)
        # remove situation where buy futures/swap and sell spot, because usually impossible open short spot position
        filtered_spreads = filter_wrong_pairs(spreads)
        return filtered_spreads

    def find_spread_by_symbol(self, symbol_1: str, exchange_1: str, exchange_type_1,
                              symbol_2: str, exchange_2: str, exchange_type_2,
                              amount_in_quote: float) -> list[SpreadData]:
        connector_1 = self.get_connector(exchange_1, exchange_type_1)
        connector_2 = self.get_connector(exchange_2, exchange_type_2)
        ticker_1 = self.ticker_fetcher.fetch_ticker_by_symbol(symbol_1, connector_1, amount_in_quote)
        ticker_2 = self.ticker_fetcher.fetch_ticker_by_symbol(symbol_2, connector_2, amount_in_quote)
        return self.founder.calculate_spreads([ticker_1, ticker_2], 0.000001, ticker_1.base_currency)

    def find_spreads_by_coin_name(self, base: str, min_spread: float,
                                  amount_in_quote: float, exchanges: SupportedExchanges) -> list[SpreadData]:
        tickers: list[FullTickerInfo] = self.ticker_fetcher.fetch_tickers_by_base(
            self.get_spot_connectors(exchanges.spot_exchanges),
            self.get_swap_connectors(exchanges.swap_exchanges),
            self.get_futures_connectors(exchanges.futures_exchanges),
            base,
            amount_in_quote
        )
        spreads :list[SpreadData] = self.founder.calculate_spreads(tickers, min_spread, base)
        filtered_spreads = filter_wrong_pairs(sorted(spreads, key=lambda x: x.spread_percent, reverse=True))
        return filtered_spreads

    def find_spreads_without_transfer(self, min_spread: float,
                                      max_spread: float,
                                      exchanges: SupportedExchanges) -> list[SpreadData]:
        spreads: list[SpreadData] = self.find_spreads(min_spread, max_spread, exchanges)
        # remove spot-spot pairs
        filtered_spreads = [
            item for item in spreads
            if not item.ticker_to_sell.spot
        ]
        return filtered_spreads


    def find_spreads(self, min_spread: float,
                     max_spread: float,
                     exchanges: SupportedExchanges) -> list[SpreadData]:
        tickers: dict[str, list[BaseTickerInfo]] = self.ticker_fetcher.fetch_tickers_in_parallel(
            self.get_spot_connectors(exchanges.spot_exchanges),
            self.get_swap_connectors(exchanges.swap_exchanges),
            self.get_futures_connectors(exchanges.futures_exchanges)
        )
        spreads = self.founder.find_arbitrage(tickers, min_spread)
        return [item for item in spreads if item.spread_percent <= max_spread]

    def get_connector(self, name: str, type: str) -> CommonConnector:
        if type == 'spot':
            return self.get_spot_connectors([name])[0]
        if type == 'swap':
            return self.get_swap_connectors([name])[0]
        if type == 'future':
            return self.get_futures_connectors([name])[0]
        raise Exception("Connector not found")

    def get_spot_connectors(self, exchanges: list[str]) -> list[SpotCommonConnector]:
        result = []
        for connector in self.all_spot_connectors:
            if connector.get_exchange_name() in exchanges:
                result.append(connector)
        return result

    def get_swap_connectors(self, exchanges: list[str]) -> list[SwapCommonConnector]:
        result = []
        for connector in self.all_swap_connectors:
            if connector.get_exchange_name() in exchanges:
                result.append(connector)
        return result

    def get_futures_connectors(self, exchanges: list[str]) -> list[FutureCommonConnector]:
        result = []
        for connector in self.all_futures_connectors:
            if connector.get_exchange_name() in exchanges:
                result.append(connector)
        return result
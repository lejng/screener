from typing import Optional

from src.arbitrage.arbitrage_founder import ArbitrageFounder
from src.arbitrage.data.spread_data import SpreadData
from src.config.common_config import CommonConfig
from src.connectors.data.full_ticker_info import FullTickerInfo
from src.connectors.data.funding_rate_info import FundingRateInfo
from src.connectors.data.base_ticker_info import BaseTickerInfo
from src.connectors.future.future_common_connector import FutureCommonConnector
from src.connectors.spot.spot_common_connector import SpotCommonConnector
from src.connectors.swap.swap_common_connector import SwapCommonConnector
from src.connectors.ticker_fetcher import TickerFetcher


# ============= Print full spread data (checking order book and funding) =============
def print_full_spreads_data(spreads: list[SpreadData]):
    for spread in spreads:
        buy = spread.ticker_to_buy
        sell = spread.ticker_to_sell
        buy_funding = get_funding_line(buy.get_funding_info())
        sell_funding = get_funding_line(sell.get_funding_info())
        funding_spread_adjustment = spread.get_funding_spread_adjustment()
        final_spread = spread.spread_percent + funding_spread_adjustment
        space = "          "
        print(f"{spread.base_currency} : spread: {spread.spread_percent}, spread with funding adjustment: {final_spread}")
        print(f"{space} buy:  [{buy.get_trading_view_name()} | price: {buy.get_best_buy_price()} | coins: {buy.get_coins_to_buy()}{buy_funding}]")
        print(f"{space} sell: [{sell.get_trading_view_name()} | price: {sell.get_best_sell_price()} | coins: {sell.get_coins_to_sell()}{sell_funding}]")

def get_funding_line(rate: Optional[FundingRateInfo]):
    if rate:
        return (
                f"| funding rate: {rate.get_funding_rate_percent()} % ," +
                f"interval: {rate.get_interval()} ," +
                f"action: {rate.get_action_for_collect_funding()} "
        )
    return ""

# ============= Print spreads data (quick search, without order book and funding) =============
def print_spreads(header: str, spreads: list[SpreadData], min_spread: float):
    print(f"======== {header} [ min spread = {min_spread}] ============")
    for spread_info in spreads:
        print_spread(spread_info)

def print_spread(spread: SpreadData):
    buy = spread.ticker_to_buy
    sell = spread.ticker_to_sell
    line = (f"{spread.base_currency} :" +
            f" {spread.spread_percent} buy:" +
            f" [{buy.get_trading_view_name()}|{buy.get_best_buy_price()}], sell:" +
            f" [{sell.get_trading_view_name()}|{sell.get_best_sell_price()}]")
    print(line)

# ============= Print funding =============
def print_top_rates(exchange_name: str, top_rates: dict[str, list[FundingRateInfo]]):
    print(f"======== Top funding rates for exchange {exchange_name} ============")
    space = "     "
    print(f"{space}=== MAX ===")
    for rate in top_rates['max']:
        print_rate(rate, space)
    print(f"{space}=== MIN ===")
    for rate in top_rates['small']:
        print_rate(rate, space)

def print_rate(rate: FundingRateInfo, space: str):
    line = (f"{space} {rate.get_symbol()}: " +
            f"rate: {rate.get_funding_rate_percent()} % ," +
            f"interval: {rate.get_interval()} ," +
            f"action: {rate.get_action_for_collect_funding()} ")
    print(line)

# ============= Utils methods =============
# remove situation where buy futures/swap and sell spot, because usually impossible open short spot position
def filter_wrong_pairs(spreads: list[SpreadData]) -> list[SpreadData]:
     return [
        item for item in spreads
        if not (item.ticker_to_sell.spot
                and (item.ticker_to_buy.swap or item.ticker_to_buy.future))
    ]

class ConsoleFacade:

    def __init__(self, all_spot_connectors: list[SpotCommonConnector],
                 all_swap_connectors: list[SwapCommonConnector],
                 all_futures_connectors: list[FutureCommonConnector]):
        self.common_config = CommonConfig('common_settings.yaml')
        self.ticker_fetcher = TickerFetcher()
        self.founder = ArbitrageFounder()
        self.all_spot_connectors: list[SpotCommonConnector] = all_spot_connectors
        self.all_swap_connectors: list[SwapCommonConnector] = all_swap_connectors
        self.all_futures_connectors: list[FutureCommonConnector] = all_futures_connectors

    def print_funding_rate_for_coin(self):
        base = input("Enter coin name (base currency): ")
        self.common_config.read_config()
        amount_in_quote = self.common_config.get_amount_in_quote()
        tickers: list[FullTickerInfo] = self.ticker_fetcher.fetch_tickers_by_base(
            [],
            self.get_swap_connectors(),
            [],
            base,
            amount_in_quote
        )
        for ticker in tickers:
            funding_info = ticker.get_funding_info()
            print(f"{ticker.get_trading_view_name()} "
                  f"| rate: {funding_info.get_funding_rate_percent()} % ," +
                  f"interval: {funding_info.get_interval()} ," +
                  f"action: {funding_info.get_action_for_collect_funding()} "
                  f"| best_buy_price: {ticker.get_best_buy_price()} "
                  f"| best_sell_price: {ticker.get_best_sell_price()} "
                  f"| coins: {ticker.get_coins_to_buy()}]")

    def print_top_funding_rates(self):
        self.common_config.read_config()
        exchanges = self.common_config.get_exchanges_for_fetch_top_fundings()
        connectors = []
        for connector in self.all_swap_connectors:
            if connector.get_exchange_name() in exchanges:
                connectors.append(connector)
        for connector in connectors:
            rates: dict[str, list[FundingRateInfo]] = connector.fetch_top_funding_rates()
            print_top_rates(connector.get_exchange_name(), rates)

    def print_all_spreads(self):
        spreads: list[SpreadData] = self.find_spreads()
        # remove situation where buy futures/swap and sell spot, because usually impossible open short spot position
        filtered_spreads = filter_wrong_pairs(spreads)
        print_spreads("All arbitrage situations", filtered_spreads, self.common_config.get_min_spread())

    def print_spread_for_entered_coin(self):
        self.common_config.reload_config()
        base = input("Enter coin name: ")
        min_spread = 0.005
        self.print_spread_for_coin(base, min_spread)

    def print_spread_for_coin(self, base: str, min_spread: float):
        amount_in_quote = self.common_config.get_amount_in_quote()
        tickers: list[FullTickerInfo] = self.ticker_fetcher.fetch_tickers_by_base(
            self.get_spot_connectors(),
            self.get_swap_connectors(),
            self.get_futures_connectors(),
            base,
            amount_in_quote
        )
        spreads :list[SpreadData] = self.founder.calculate_spreads(tickers, min_spread, base)
        filtered_spreads = filter_wrong_pairs(sorted(spreads, key=lambda x: x.spread_percent, reverse=True))
        print_full_spreads_data(filtered_spreads)

    def print_spreads_without_transfer(self):
        spreads: list[SpreadData] = self.find_spreads()
        # remove spot-spot pairs
        filtered_spreads = [
            item for item in spreads
            if not item.ticker_to_sell.spot
        ]
        print_spreads("Arbitrage situations without SPOT-SPOT pairs", filtered_spreads, self.common_config.get_min_spread())

    def find_spreads(self) -> list[SpreadData]:
        self.common_config.reload_config()
        tickers: dict[str, list[BaseTickerInfo]] = self.ticker_fetcher.fetch_tickers_in_parallel(
            self.get_spot_connectors(),
            self.get_swap_connectors(),
            self.get_futures_connectors()
        )
        return self.founder.find_arbitrage(tickers, self.common_config.get_min_spread())

    def get_spot_connectors(self) -> list[SpotCommonConnector]:
        exchanges = self.common_config.get_spot_exchanges()
        result = []
        for connector in self.all_spot_connectors:
            if connector.get_exchange_name() in exchanges:
                result.append(connector)
        return result

    def get_swap_connectors(self) -> list[SwapCommonConnector]:
        exchanges = self.common_config.get_swap_exchanges()
        result = []
        for connector in self.all_swap_connectors:
            if connector.get_exchange_name() in exchanges:
                result.append(connector)
        return result

    def get_futures_connectors(self) -> list[FutureCommonConnector]:
        exchanges = self.common_config.get_futures_exchanges()
        result = []
        for connector in self.all_futures_connectors:
            if connector.get_exchange_name() in exchanges:
                result.append(connector)
        return result

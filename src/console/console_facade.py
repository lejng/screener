from typing import Optional

from src.arbitrage.arbitrage_facade import ArbitrageFacade
from src.arbitrage.data.spread_data import SpreadData
from src.arbitrage.data.supported_exchanges import SupportedExchanges
from src.config.common_config import CommonConfig
from src.connectors.data.full_ticker_info import FullTickerInfo
from src.connectors.data.funding_rate_info import FundingRateInfo


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

class ConsoleFacade:

    def __init__(self, arbitrage_facade: ArbitrageFacade):
        self.common_config = CommonConfig('common_settings.yaml')
        self.arbitrage_facade = arbitrage_facade

    def print_funding_rate_for_coin(self):
        base = input("Enter coin name (base currency): ")
        self.common_config.read_config()
        amount_in_quote = self.common_config.get_amount_in_quote()
        tickers: list[FullTickerInfo] = self.arbitrage_facade.get_full_ticker_info_for_swap_coin(base, amount_in_quote, self.common_config.get_swap_exchanges())
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
        for exchange in exchanges:
            rates: dict[str, list[FundingRateInfo]] = self.arbitrage_facade.get_top_funding_rates(exchange)
            print_top_rates(exchange, rates)

    def print_all_spreads(self):
        self.common_config.reload_config()
        exchanges: SupportedExchanges = self.get_supported_exchanges()
        spreads: list[SpreadData] = self.arbitrage_facade.find_all_spreads(self.common_config.get_min_spread(), self.common_config.get_max_spread(), exchanges)
        print_spreads("All arbitrage situations", spreads, self.common_config.get_min_spread())

    def print_spread_for_entered_coin(self):
        self.common_config.reload_config()
        base = input("Enter coin name: ")
        min_spread = 0.005
        self.print_spread_for_coin(base, min_spread)

    def print_spread_for_coin(self, base: str, min_spread: float):
        self.common_config.reload_config()
        amount_in_quote = self.common_config.get_amount_in_quote()
        exchanges: SupportedExchanges = self.get_supported_exchanges()
        spreads: list[SpreadData] = self.arbitrage_facade.find_spread_for_coin(
            base,
            min_spread,
            amount_in_quote,
            exchanges
        )
        print_full_spreads_data(spreads)

    def print_spreads_without_transfer(self):
        self.common_config.reload_config()
        exchanges: SupportedExchanges = self.get_supported_exchanges()
        spreads: list[SpreadData] = self.arbitrage_facade.find_spreads_without_transfer(
            self.common_config.get_min_spread(),
            self.common_config.get_max_spread(),
            exchanges
        )
        print_spreads("Arbitrage situations without SPOT-SPOT pairs", spreads, self.common_config.get_min_spread())

    def get_supported_exchanges(self) -> SupportedExchanges:
        return SupportedExchanges(
            self.common_config.get_spot_exchanges(),
            self.common_config.get_swap_exchanges(),
            self.common_config.get_futures_exchanges()
        )

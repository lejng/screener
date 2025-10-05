from fastapi import APIRouter
from pydantic import BaseModel

from src.arbitrage.arbitrage_facade import ArbitrageFacade
from src.arbitrage.data.spread_data import SpreadData
from src.arbitrage.data.supported_exchanges import SupportedExchanges
from src.connectors.connectors_container import all_spot_connectors
from src.connectors.connectors_container import all_swap_connectors
from src.connectors.connectors_container import all_futures_connectors
from src.connectors.data.base_ticker_info import BaseTickerInfo

arbitrage_facade: ArbitrageFacade = ArbitrageFacade(all_spot_connectors, all_swap_connectors, all_futures_connectors)

router = APIRouter(
    prefix="/spreads",       # common prefix for all routers
    tags=["spreads"]         # for documentation (Swagger)
)

class SpreadsQuery(BaseModel):
    min_spread: float = 1
    max_spread: float = 100
    spot_exchanges: list[str] = ['BYBIT','GATEIO','KUCOIN','BINANCE','MEXC','BITGET','OKX']
    swap_exchanges: list[str] = ['BYBIT','GATEIO','KUCOIN','HYPERLIQUID','PARADEX','BINANCE','MEXC','BITGET','OKX']
    futures_exchanges: list[str] = []

class SpreadCoinQuery(BaseModel):
    base: str = 'BTC'
    min_spread: float = 0.001
    amount_in_quote: float = 100
    spot_exchanges: list[str] = ['BYBIT','GATEIO','KUCOIN','BINANCE','MEXC','BITGET','OKX']
    swap_exchanges: list[str] = ['BYBIT','GATEIO','KUCOIN','HYPERLIQUID','PARADEX','BINANCE','MEXC','BITGET','OKX']
    futures_exchanges: list[str] = []

@router.post("")
def get_spreads(query: SpreadsQuery):
    exchanges = SupportedExchanges(
        query.spot_exchanges,
        query.swap_exchanges,
        query.futures_exchanges
    )
    # create response class
    spreads = arbitrage_facade.find_all_spreads(query.min_spread, query.max_spread, exchanges)
    return [convert_to_full_spread_response(spread) for spread in spreads]

@router.post("/no-transfer")
def get_spreads(query: SpreadsQuery):
    exchanges = SupportedExchanges(
        query.spot_exchanges,
        query.swap_exchanges,
        query.futures_exchanges
    )
    # create response class
    spreads = arbitrage_facade.find_spreads_without_transfer(query.min_spread, query.max_spread, exchanges)
    return [convert_to_full_spread_response(spread) for spread in spreads]

@router.post("/by_coin_name")
def find_spread_for_coin(query: SpreadCoinQuery):
    exchanges = SupportedExchanges(
        query.spot_exchanges,
        query.swap_exchanges,
        query.futures_exchanges
    )
    spreads = arbitrage_facade.find_spread_for_coin(query.base, query.min_spread, query.amount_in_quote, exchanges)
    return [convert_to_full_spread_response(spread) for spread in spreads]

def convert_to_full_spread_response(spread_data: SpreadData) -> dict:
    return {
        "base_currency": spread_data.base_currency,
        "spread_percent": spread_data.spread_percent,
        "ticker_to_buy": convert_to_ticker_response(spread_data.ticker_to_buy),
        "ticker_to_sell": convert_to_ticker_response(spread_data.ticker_to_sell)
    }

def convert_to_ticker_response(ticker: BaseTickerInfo) -> dict:
    response_ticker = {
        "trading_view_name": ticker.get_trading_view_name(),
        "symbol": ticker.get_symbol(),
        "base_currency": ticker.base_currency,
        "quote_currency": ticker.quote_currency,
        "exchange_name": ticker.exchange_name,
        "market_type": ticker.get_market_type(),
        "best_buy_price": ticker.get_best_buy_price(),
        "best_sell_price": ticker.get_best_sell_price(),
        "coins_to_buy": ticker.get_coins_to_buy(),
        "coins_to_sell": ticker.get_coins_to_sell()
    }
    funding = ticker.get_funding_info()
    if funding is not None:
        response_ticker["funding_info"] = {
            "rate": funding.get_funding_rate_percent(),
            "interval": funding.get_interval(),
            "action_for_collect_funding": funding.get_action_for_collect_funding()
        }
    return response_ticker

from fastapi import APIRouter

from src.arbitrage.arbitrage_facade import ArbitrageFacade
from src.connectors.connectors_container import all_swap_connectors
from src.connectors.data.funding_rate_info import FundingRateInfo

arbitrage_facade: ArbitrageFacade = ArbitrageFacade([], all_swap_connectors, [])

router = APIRouter(
    prefix="/api/rates",       # common prefix for all routers
    tags=["rates"]         # for documentation (Swagger)
)

@router.get("/top")
def get_top_rates():
    exchanges = ['BYBIT','GATEIO','HYPERLIQUID','BINANCE','BITGET','OKX']
    rates_per_exchange: dict[str, dict] = {}
    for exchange in exchanges:
        rates: dict[str, list[FundingRateInfo]] = arbitrage_facade.get_top_funding_rates(exchange)
        rates_per_exchange[exchange] = convert_to_funding_response_map(rates)
    return rates_per_exchange

def convert_to_funding_response_map(rates: dict[str, list[FundingRateInfo]]) -> dict:
    min_rates: list[FundingRateInfo] = rates['small']
    max_rates: list[FundingRateInfo] = rates['max']
    return {
            'max_rates': [convert_funding_response(rate) for rate in max_rates],
            'min_rates': [convert_funding_response(rate) for rate in min_rates]
    }

def convert_funding_response(funding: FundingRateInfo) -> dict:
    return {
            "symbol": funding.get_symbol(),
            "rate": funding.get_funding_rate_percent(),
            "interval": funding.get_interval(),
            "action_for_collect_funding": funding.get_action_for_collect_funding()
        }
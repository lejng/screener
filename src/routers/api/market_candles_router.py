from fastapi import APIRouter

from src.arbitrage.arbitrage_facade import ArbitrageFacade
from src.connectors.connectors_container import all_spot_connectors, all_swap_connectors, all_futures_connectors

arbitrage_facade: ArbitrageFacade = ArbitrageFacade(all_spot_connectors, all_swap_connectors, all_futures_connectors)

router = APIRouter(
    prefix="/api/candles",       # common prefix for all routers
    tags=["candles"]         # for documentation (Swagger)
)

@router.get("")
def get_candles(symbol: str, exchange: str, exchange_type: str, limit: int = 50, timeframe: str = '5m'):
    return arbitrage_facade.fetch_candles(symbol, exchange, exchange_type, limit, timeframe)
from dataclasses import dataclass

from src.connectors.common import TickerData


@dataclass
class SpreadData:
    ticker_to_buy: TickerData
    ticker_to_sell: TickerData
    spread_percent: float
    base_currency: str

def calculate_buy_sell_spread_percent(buy: float, sell: float):
    if buy <= 0 or sell <= 0:
        return 0
        # if sell <= buy:
        #    return 0
    try:
        spread_percent = ((sell - buy) / buy) * 100
        return spread_percent
    except TypeError:
        return 0
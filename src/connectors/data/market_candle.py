from dataclasses import dataclass


@dataclass
class MarketCandle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

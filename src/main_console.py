from src.connectors.binance_connector import BinanceConnector
from src.connectors.bybit_connector import BybitConnector
from src.connectors.common_connector import CommonConnector
from src.connectors.gate_connector import GateConnector
from src.connectors.kucoin_connector import KucoinConnector
from src.connectors.mexc_connector import MexcConnector
from src.console.console_facade import ConsoleFacade

all_connectors: list[CommonConnector] = [
        BybitConnector(),
        GateConnector(),
        MexcConnector(),
        BinanceConnector(),
        KucoinConnector()
    ]

console_facade = ConsoleFacade(all_connectors)
while True:
    print("1 - Exit")
    print("2 - Show all types of spreads (spot-spot, spot-swap, spot-futures, swap-swap, all combinations swap and futures)")
    print("3 - Show spreads without transferring (spot-swap, spot-futures, swap-swap, all combinations swap and futures)")
    print("4 - Show top fundings")
    print("5 - Show funding by selected coin")
    print("6 - Show volume weighted average price")

    command = input("Enter command: ")
    if command == '1':
        break
    if command == '2':
        console_facade.print_all_spreads()
    if command == '3':
        console_facade.print_spreads_without_transfer()
    if command == '4':
        console_facade.print_top_funding_rates()
    if command == '5':
        console_facade.print_funding_rate_by_quote()
    if command == '6':
        console_facade.print_volume_weighted_average_price()
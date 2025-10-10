from src.arbitrage.arbitrage_facade import ArbitrageFacade
from src.console.console_facade import ConsoleFacade
from src.connectors.connectors_container import all_spot_connectors, all_swap_connectors, all_futures_connectors

arbitrage_facade = ArbitrageFacade(all_spot_connectors, all_swap_connectors, all_futures_connectors)
console_facade = ConsoleFacade(arbitrage_facade)
while True:
    print("1 - Exit")
    print("2 - Show all types of spreads (spot-spot, spot-swap, spot-futures, swap-swap, all combinations swap and futures)")
    print("3 - Show spreads without transferring (spot-swap, spot-futures, swap-swap, all combinations swap and futures)")
    print("4 - Show spread for coin")
    print("5 - Show top fundings")
    print("6 - Show funding by selected coin")

    command = input("Enter command: ")
    try:
        if command == '1':
            break
        if command == '2':
            console_facade.print_all_spreads()
        if command == '3':
            console_facade.print_spreads_without_transfer()
        if command == '4':
            console_facade.print_spread_for_entered_coin()
        if command == '5':
            console_facade.print_top_funding_rates()
        if command == '6':
            console_facade.print_funding_rate_for_coin()
    except Exception as e:
        print(f"Unexpected error: {e}")
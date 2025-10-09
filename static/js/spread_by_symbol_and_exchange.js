async function renderArbitrageData() {
    const spinner = document.getElementById("spinner");
    spinner.style.display = "flex";
    let data = [];
    if (window.hiddenParams) {
        const params = window.hiddenParams;
        const link = `/api/spreads/by_symbol_and_exchange?symbol_1=${params.symbol_1}&exchange_1=${params.exchange_1}&exchange_type_1=${params.exchange_type_1}&symbol_2=${params.symbol_2}&exchange_2=${params.exchange_2}&exchange_type_2=${params.exchange_type_2}&amount_in_quote=${params.amount_in_quote}`;

        try {
            const response = await fetch(link, {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            });
            if (!response.ok) throw new Error("Error request");
            data = await response.json();
        } catch (err) {
            console.error(err);
            alert("Cannot load spread info");
            spinner.style.display = "none";
            return;
        }
    } else {
        console.log("Error getting hidden parameters");
        return;
    }

    const container = document.getElementById('arbitrageData');
    container.innerHTML = ''; // Очищаем контейнер перед добавлением новых данных

     if (!data || data.length === 0) {
        alert("Spread data absent");
     }

    data.forEach(opportunity => {
        const spreadClass = opportunity.spread_percent > 0 ? 'bg-success' : 'bg-danger';

        // Форматирование чисел с проверкой на существование
        const formatNumber = (num, decimals = 8) => {
            if (num === undefined || num === null) return 'N/A';
            return num.toFixed(decimals);
        };

        const cardHtml = `
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span>${opportunity.base_currency} Arbitrage Opportunity</span>
                        <span class="badge ${spreadClass} spread-badge">Spread: ${formatNumber(opportunity.spread_percent, 2)}%</span>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <!-- Buy Section -->
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header bg-success text-white">
                                        <i class="bi bi-arrow-down-circle"></i> Buy on ${opportunity.ticker_to_buy.exchange_name}
                                        <span class="badge bg-light text-dark exchange-badge ms-2">${opportunity.ticker_to_buy.market_type}</span>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-6">
                                                <strong>Symbol:</strong>
                                            </div>
                                            <div class="col-6">
                                                ${opportunity.ticker_to_buy.trading_view_name}
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-6">
                                                <strong>Best Buy Price:</strong>
                                            </div>
                                            <div class="col-6">
                                                $${formatNumber(opportunity.ticker_to_buy.best_buy_price)}
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-6">
                                                <strong>Coins to Buy:</strong>
                                            </div>
                                            <div class="col-6">
                                                ${formatNumber(opportunity.ticker_to_buy.coins_to_buy, 4)}
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-6">
                                                <strong>Position Amount:</strong>
                                            </div>
                                            <div class="col-6">
                                                $${formatNumber(opportunity.ticker_to_buy.position_amount, 2)}
                                            </div>
                                        </div>
                                        <!-- Funding Info (if available) -->
                                        ${opportunity.ticker_to_buy.funding_info ? `
                                        <div class="funding-info mt-3">
                                            <h6>Funding Information</h6>
                                            <div class="row">
                                                <div class="col-6">
                                                    <strong>Rate:</strong>
                                                </div>
                                                <div class="col-6">
                                                    ${opportunity.ticker_to_buy.funding_info.rate.toFixed(6)}%
                                                </div>
                                            </div>
                                            <div class="row">
                                                <div class="col-6">
                                                    <strong>Interval:</strong>
                                                </div>
                                                <div class="col-6">
                                                    ${opportunity.ticker_to_buy.funding_info.interval}
                                                </div>
                                            </div>
                                            <div class="row">
                                                <div class="col-6">
                                                    <strong>Action:</strong>
                                                </div>
                                                <div class="col-6">
                                                    ${opportunity.ticker_to_buy.funding_info.action_for_collect_funding}
                                                </div>
                                            </div>
                                        </div>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>

                            <!-- Sell Section -->
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header bg-danger text-white">
                                        <i class="bi bi-arrow-up-circle"></i> Sell on ${opportunity.ticker_to_sell.exchange_name}
                                        <span class="badge bg-light text-dark exchange-badge ms-2">${opportunity.ticker_to_sell.market_type}</span>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-6">
                                                <strong>Symbol:</strong>
                                            </div>
                                            <div class="col-6">
                                                ${opportunity.ticker_to_sell.trading_view_name}
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-6">
                                                <strong>Best Sell Price:</strong>
                                            </div>
                                            <div class="col-6">
                                                $${formatNumber(opportunity.ticker_to_sell.best_sell_price)}
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-6">
                                                <strong>Coins to Sell:</strong>
                                            </div>
                                            <div class="col-6">
                                                ${formatNumber(opportunity.ticker_to_sell.coins_to_sell, 4)}
                                            </div>
                                        </div>
                                        <div class="row">
                                            <div class="col-6">
                                                <strong>Position Amount:</strong>
                                            </div>
                                            <div class="col-6">
                                                $${formatNumber(opportunity.ticker_to_sell.position_amount, 2)}
                                            </div>
                                        </div>

                                        <!-- Funding Info (if available) -->
                                        ${opportunity.ticker_to_sell.funding_info ? `
                                        <div class="funding-info mt-3">
                                            <h6>Funding Information</h6>
                                            <div class="row">
                                                <div class="col-6">
                                                    <strong>Rate:</strong>
                                                </div>
                                                <div class="col-6">
                                                    ${opportunity.ticker_to_sell.funding_info.rate.toFixed(6)}%
                                                </div>
                                            </div>
                                            <div class="row">
                                                <div class="col-6">
                                                    <strong>Interval:</strong>
                                                </div>
                                                <div class="col-6">
                                                    ${opportunity.ticker_to_sell.funding_info.interval}
                                                </div>
                                            </div>
                                            <div class="row">
                                                <div class="col-6">
                                                    <strong>Action:</strong>
                                                </div>
                                                <div class="col-6">
                                                    ${opportunity.ticker_to_sell.funding_info.action_for_collect_funding}
                                                </div>
                                            </div>
                                        </div>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML += cardHtml;
    });
    spinner.style.display = "none";
}

// Initialize the page with data
document.addEventListener('DOMContentLoaded', function() {
    renderArbitrageData();
});
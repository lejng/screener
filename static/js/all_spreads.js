setLoadingState(false);

function getFilters() {
  return {
    minSpread: parseFloat(document.getElementById("minSpread").value),
    maxSpread: parseFloat(document.getElementById("maxSpread").value),
    amountInUsdt: parseFloat(document.getElementById("amountInUsdt").value),
    spot: getSelectedValues("exchanges_spot"),
    swap: getSelectedValues("exchanges_swap"),
    future: getSelectedValues("exchanges_future"),
    noTransfer: document.getElementById("noTransfer").checked,
  };
}

function buildRequestBody(filters) {
  return {
    min_spread: filters.minSpread,
    max_spread: filters.maxSpread,
    spot_exchanges: filters.spot,
    swap_exchanges: filters.swap,
    futures_exchanges: filters.future,
  };
}

// reuse common setLoadingState(spinnerId, buttonId)

function renderRows(table, data, amountInUsdt) {
  const tbody = table.querySelector("tbody");
  tbody.innerHTML = "";
  data.forEach((item) => {
    const tickerToBuy = `${item.ticker_to_buy.trading_view_name}`;
    const tickerToSell = `${item.ticker_to_sell.trading_view_name}`;
    const link = `/spread_by_symbol_and_exchange?symbol_1=${item.ticker_to_buy.symbol}&exchange_1=${item.ticker_to_buy.exchange_name}&exchange_type_1=${item.ticker_to_buy.market_type}&symbol_2=${item.ticker_to_sell.symbol}&exchange_2=${item.ticker_to_sell.exchange_name}&exchange_type_2=${item.ticker_to_sell.market_type}&amount_in_quote=${amountInUsdt}`;

    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.base_currency}</td>
      <td>${item.spread_percent.toFixed(2)}%</td>
      <td>${tickerToBuy}</td>
      <td>${tickerToSell}</td>
      <td><a href="${link}" target="_blank">Open more</a></td>
    `;
    tbody.appendChild(row);
  });
}

async function fetchEndpoint(endpoint, body) {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error("Error request");
  return await response.json();
}

async function fetchSpreads() {
  const tableContainer = document.getElementById("table-container");
  const table = document.getElementById("spreads-table");
  const filters = getFilters();
  const body = buildRequestBody(filters);
  const endpoint = filters.noTransfer ? "/api/spreads/no-transfer" : "/api/spreads";
  try {
    setLoadingState(true);
    const data = await fetchEndpoint(endpoint, body);
    renderRows(table, data, filters.amountInUsdt);
    tableContainer.style.display = "block";
  } catch (err) {
    console.error(err);
    alert("Cannot load spread info");
  } finally {
    setLoadingState(false);
  }
}
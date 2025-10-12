// reuse common setLoadingState

function formatNumber(num, decimals = 8) {
  if (num === undefined || num === null) return 'N/A';
  return num.toFixed(decimals);
}

function buildApiLink(params) {
  return `/api/spreads/by_symbol_and_exchange?symbol_1=${params.symbol_1}&exchange_1=${params.exchange_1}&exchange_type_1=${params.exchange_type_1}&symbol_2=${params.symbol_2}&exchange_2=${params.exchange_2}&exchange_type_2=${params.exchange_type_2}&amount_in_quote=${params.amount_in_quote}`;
}

function renderCard(container, opportunity) {
  renderSpreadCard(container, opportunity);
}

async function renderArbitrageData() {
  setLoadingState(true);
  try {
    if (!window.hiddenParams) {
      console.log("Error getting hidden parameters");
      return;
    }
    const link = buildApiLink(window.hiddenParams);
    const response = await fetch(link, { method: "GET", headers: { "Content-Type": "application/json" } });
    if (!response.ok) throw new Error("Error request");
    const data = await response.json();
    const container = document.getElementById('arbitrageData');
    container.innerHTML = '';
    if (!data || data.length === 0) {
      container.innerHTML = `<div class="alert alert-warning" role="alert">No spreads found for trading amount: ${window.hiddenParams.amount_in_quote}</div>`;
      return;
    }
    data.forEach((opportunity) => renderCard(container, opportunity));
  } catch (err) {
    console.error(err);
    const container = document.getElementById('arbitrageData');
    if (container) {
      container.innerHTML = '<div class="alert alert-danger" role="alert">Failed to load spread info.</div>';
    }
  } finally {
    setLoadingState(false);
    renderSpreadChart();
  }
}

document.addEventListener('DOMContentLoaded', function () {
  renderArbitrageData();
});
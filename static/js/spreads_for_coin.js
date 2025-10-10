setLoadingState(false);

function getFilters() {
  return {
    coin: document.getElementById("coin").value,
    amountInUsdt: parseFloat(document.getElementById("amountInUsdt").value),
    spot: getSelectedValues("exchanges_spot"),
    swap: getSelectedValues("exchanges_swap"),
    future: getSelectedValues("exchanges_future"),
  };
}

// reuse common setLoadingState

function formatNumber(num, decimals = 8) {
  if (num === undefined || num === null) return 'N/A';
  return num.toFixed(decimals);
}

function buildRequestBody(filters) {
  return {
    base: filters.coin,
    amount_in_quote: filters.amountInUsdt,
    spot_exchanges: filters.spot,
    swap_exchanges: filters.swap,
    futures_exchanges: filters.future,
  };
}

function renderCard(container, opportunity) {
  renderSpreadCard(container, opportunity);
}

async function fetchSpreads() {
  const filters = getFilters();
  const body = buildRequestBody(filters);
  try {
    setLoadingState(true);
    const response = await fetch("/api/spreads/by_coin_name", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) throw new Error("Error request");
    const data = await response.json();
    const container = document.getElementById('arbitrageData');
    container.innerHTML = '';
    if (!data || data.length === 0) {
      container.innerHTML = '<div class="alert alert-warning" role="alert">No spreads found.</div>';
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
  }
}
function createChart(chartContainerName, data) {
  const chart = LightweightCharts.createChart(
    document.getElementById(chartContainerName),
    {
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      }
    }
  );

  const lineSeries = chart.addSeries(LightweightCharts.LineSeries, {
    color: '#2962FF',
    priceFormat: {
      type: 'price',
      precision: 4,
      minMove: 0.0001,
    }
  });
  lineSeries.setData(data);

  chart.timeScale().fitContent();
  window.addEventListener("resize", () => {
    chart.resize(window.innerWidth, window.innerHeight);
  });
}


function buildLinkForFetchCandles(symbol, exchange, exchange_type) {
  const limit = 200
  const timeframe = '5m'
  return `/api/candles?symbol=${symbol}&exchange=${exchange}&exchange_type=${exchange_type}&limit=${limit}&timeframe=${timeframe}`;
}

async function renderSpreadChart() {
  if (!window.hiddenParams) {
    console.log("Error getting hidden parameters");
    return;
  }
  const params = window.hiddenParams
  const title = `Spread chart: ${params.symbol_1} (${params.exchange_1}) / ${params.symbol_2} (${params.exchange_2})`;
  const titleContainer = document.getElementById('chartTitle')
  titleContainer.innerHTML = `<div class="alert alert-primary" role="alert">${title}</div>`
  const ohlcvData1Response = await fetch(buildLinkForFetchCandles(params.symbol_1, params.exchange_1, params.exchange_type_1), { method: "GET", headers: { "Content-Type": "application/json" } });
  const ohlcvData2Response = await fetch(buildLinkForFetchCandles(params.symbol_2, params.exchange_2, params.exchange_type_2), { method: "GET", headers: { "Content-Type": "application/json" } });
  const ohlcvData1 = await ohlcvData1Response.json();
  const ohlcvData2 = await ohlcvData2Response.json();
  const data = syncAndCalculateSpread(ohlcvData1, ohlcvData2).map((candle, index) => {
    return { time: normalizeTimeForChart(candle.timestamp), value: candle.close }
  });
  createChart('chartContainer', data)

}

// this is temporary solution in plan to create endpoint and fetch data from backend
function syncAndCalculateSpread(assetAData, assetBData) {
  const assetBMap = new Map();
  assetBData.forEach(candle => {
    assetBMap.set(candle.timestamp, candle);
  });

  const result = [];

  assetAData.forEach(candleA => {
    const candleB = assetBMap.get(candleA.timestamp);

    if (candleB) {
      if (candleB.open === 0 || candleB.high === 0 || candleB.low === 0 || candleB.close === 0) {
        console.warn(`Missed candle with null values: ${candleA.timestamp}`);
        return;
      }

      result.push({
        timestamp: candleA.timestamp,
        open: candleA.open / candleB.open,
        high: candleA.high / candleB.high,
        low: candleA.low / candleB.low,
        close: candleA.close / candleB.close
      });
    }
  });

  console.log(`Synchronised ${result.length} candles from ${assetAData.length}`);
  return result;
}

function normalizeTimeForChart(timestamp) {
  if (!timestamp) return null;

  if (typeof timestamp === 'string') {
    const date = new Date(timestamp);
    if (!isNaN(date.getTime())) {
      return Math.floor(date.getTime() / 1000);
    }
    return timestamp;
  }

  if (timestamp > 1000000000000) {
    return Math.floor(timestamp / 1000);
  }

  return timestamp;
}
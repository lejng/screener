async function fetchSpreads() {
        const spinner = document.getElementById("spinner");
        spinner.style.display = "flex";
        const tableContainer = document.getElementById("table-container");
        const table = document.getElementById("spreads-table");

        // get filter values
        const coin = document.getElementById("coin").value;
        const amountInUsdt = parseFloat(document.getElementById("amountInUsdt").value);
        const selectedExchangesSpot = Array.from(
          document.getElementById("exchanges_spot").selectedOptions
        ).map((opt) => opt.value);
        const selectedExchangesSwap = Array.from(
          document.getElementById("exchanges_swap").selectedOptions
        ).map((opt) => opt.value);
        const selectedExchangesFuture = Array.from(
          document.getElementById("exchanges_future").selectedOptions
        ).map((opt) => opt.value);

        const bodyData = {
          base: coin,
          amount_in_quote: amountInUsdt,
          spot_exchanges: selectedExchangesSpot,
          swap_exchanges: selectedExchangesSwap,
          futures_exchanges: selectedExchangesFuture,
        };

        try {
          const response = await fetch("/api/spreads/by_coin_name", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(bodyData),
          });

          if (!response.ok) throw new Error("Error request");

          const data = await response.json();
          const tbody = table.querySelector("tbody");
          tbody.innerHTML = "";

          data.forEach((item) => {
            let ticker_to_buy = `${item.ticker_to_buy.trading_view_name}<br>
            price: ${item.ticker_to_buy.best_buy_price}<br>
            coins: ${item.ticker_to_buy.coins_to_buy}<br>
            `;
            let ticker_to_sell = `${item.ticker_to_sell.trading_view_name}<br>
            price: ${item.ticker_to_sell.best_sell_price}<br>
            coins: ${item.ticker_to_sell.coins_to_sell}<br>
            `;
            if (item.ticker_to_buy?.funding_info !== undefined) {
                ticker_to_buy += `
                funding rate: ${item.ticker_to_buy.funding_info.rate} %<br>
                funding interval: ${item.ticker_to_buy.funding_info.interval}<br>
                funding action: ${item.ticker_to_buy.funding_info.action_for_collect_funding}<br>
                `
            }

            if (item.ticker_to_sell?.funding_info !== undefined) {
                ticker_to_sell += `
                funding rate: ${item.ticker_to_sell.funding_info.rate} %<br>
                funding interval: ${item.ticker_to_sell.funding_info.interval}<br>
                funding action: ${item.ticker_to_sell.funding_info.action_for_collect_funding}<br>
                `
            }

            const row = document.createElement("tr");
            row.innerHTML = `
              <td>${item.base_currency}</td>
              <td>${item.spread_percent.toFixed(5)}%</td>
              <td>${ticker_to_buy}</td>
              <td>${ticker_to_sell}</td>
            `;
            tbody.appendChild(row);
          });

          spinner.style.display = "none";
          tableContainer.style.display = "block";
        } catch (err) {
          console.error(err);
          alert("Cannot load spread info");
          spinner.style.display = "none";
        }
      }

     spinner.style.display = "none";
# 📊 Spread Scanner: Quantitative Arbitrage Intelligence

A full-stack analytical platform designed to identify and visualize arbitrage opportunities across 10+ cryptocurrency exchanges. This tool bridges the gap between raw data and actionable trading insights by accounting for market-specific factors like funding rates and instrument types.

## 🚀 Key Features

* **Cross-Market Analysis**: Advanced comparison engine supporting **Spot-to-Swap**, **Swap-to-Swap**, and **Future** price discrepancies.
* **Funding Rate Analysis**: Integrated monitoring of funding rates across perpetual swaps to identify complex arbitrage opportunities and prevent "profit bleeding" during trade holding.
* **Historical Spreads**: Time-series visualization of spread movements via interactive charts for optimized entry and exit timing.
* **Multi-Exchange Connectivity**: Real-time data integration with major platforms including **Binance, Bybit, Gate.io, Hyperliquid, OKX**, and more.

## 🛠 Tech Stack

* **Backend**: Python 3.x, FastAPI, Uvicorn.
* **Logic**: CCXT (Exchange connectivity).
* **Frontend**: Interactive Web UI.
* **DevOps**: Docker & Docker Compose.

## 📈 Logic Overview (Funding-Aware Arbitrage)

The system goes beyond simple price comparison; it evaluates the actual viability of a trade.


## Commands (os windows)

### 1. Determinate is it virt env or not
```
where pip
```

### 2. Activate virtual env or create virtual env
activate
```
.venv\Scripts\activate
```
create:
```
python -m venv .venv
```

### 3. Install/remove dependencies
```
pip install -r requirements.txt

pip uninstall -r requirements.txt
```

### 4. Deactivate virtual env
```
deactivate
```

### 5. How to run console app
```
python -m src.main_console
```

### 6. How to run web app (dev mode)
```
uvicorn src.main_web:app --port 8000 --reload
uvicorn src.main_web:app --port 8000
```

### 7. Endpoints
```
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
```

## Docker Commands

### 8. Run with Docker Compose
```bash
# Build and start
docker-compose up --build

# Start in background
docker-compose up -d

# Start without rebuild
docker-compose up
```

### 9. Stop Docker containers
```bash
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

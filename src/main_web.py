from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from src.routers.ui import pages_router
from src.routers.api import spreads_router, rates_router, market_candles_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Connect controllers
app.include_router(spreads_router.router)
app.include_router(rates_router.router)
app.include_router(market_candles_router.router)
app.include_router(pages_router.router)
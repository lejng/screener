from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from src.routers import spreads_router, html_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Connect controllers
app.include_router(spreads_router.router)
app.include_router(html_router.router)
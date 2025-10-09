from json import dumps

from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

router = APIRouter(
    prefix="",       # common prefix for all routers
    tags=["html"]         # for documentation (Swagger)
)

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@router.get("/spreads", response_class=HTMLResponse)
def spreads_page(request: Request):
    return templates.TemplateResponse("all_spreads.html", {"request": request})

@router.get("/spreads_for_coin", response_class=HTMLResponse)
def main_page(request: Request):
    return templates.TemplateResponse("spreads_for_coin.html", {"request": request})

@router.get("/spread_by_symbol_and_exchange", response_class=HTMLResponse)
def find_spread_by_symbol_and_exchange(request: Request,
                                       symbol_1: str,
                                       exchange_1: str,
                                       exchange_type_1,
                                       symbol_2,
                                       exchange_2: str,
                                       exchange_type_2,
                                       amount_in_quote: float = 100):
    hidden_params = {
        "symbol_1": symbol_1,
        "exchange_1": exchange_1,
        "exchange_type_1": exchange_type_1,
        "symbol_2": symbol_2,
        "exchange_2": exchange_2,
        "exchange_type_2": exchange_type_2,
        "amount_in_quote": amount_in_quote
    }
    return templates.TemplateResponse("spread_by_symbol_and_exchange.html", {"request": request,  "hidden_params_json": dumps(hidden_params)})
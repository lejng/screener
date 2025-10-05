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

@router.get("/page/spreads", response_class=HTMLResponse)
def main_page(request: Request):
    return templates.TemplateResponse("all_spreads.html", {"request": request})

@router.get("/page/spreads_for_coin", response_class=HTMLResponse)
def main_page(request: Request):
    return templates.TemplateResponse("spreads_for_coin.html", {"request": request})
import os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

router = APIRouter(prefix="/html", tags=["html"])

# 设置模板目录
templates = Jinja2Templates(directory="templates/html")


@router.get("/chat_dome", response_class=HTMLResponse)
async def read_root(request: Request):
    # 返回 HTML 页面
    return templates.TemplateResponse("chat_dome.html", {"request": request})

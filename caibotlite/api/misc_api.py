import nonebot
from fastapi import FastAPI
from starlette.responses import JSONResponse

from caibotlite.constants import BOT_APPID

app = nonebot.get_app()
app: FastAPI


@app.get("/ping")
async def ping():
    return JSONResponse({"result": "pong"})


@app.get(f"/{BOT_APPID}.json")
async def qq_url_check():
    return JSONResponse({"bot_appid": {BOT_APPID}})

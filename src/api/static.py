import nonebot
from fastapi import FastAPI, HTTPException
from starlette.responses import RedirectResponse, JSONResponse

app = nonebot.get_app()
app: FastAPI

@app.get("/wiki/{website}/{keyword}")
async def wiki_proxy(website: str, keyword: str):
    if website == "gg":
        search_url = f"http://wiki.terraria.ink/?search={keyword}"
    elif website == "calamity":
        base_url = "https://calamity.huijiwiki.com"
        search_url = f"{base_url}/index.php?search={keyword}"
    else:
        raise HTTPException(status_code=404, detail="Website not supported")

    return RedirectResponse(url=search_url)

@app.get("/ping")
async def ping():
    return JSONResponse({"result": "pong"})

@app.get("/102256264.json")
async def qq_url_check():
    return JSONResponse({"bot_appid": 102256264})
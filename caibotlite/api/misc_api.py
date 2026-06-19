import nonebot
from fastapi import FastAPI
from starlette.responses import JSONResponse, HTMLResponse

from caibotlite.constants import BOT_APPID

app = nonebot.get_app()
app: FastAPI


@app.get("/ping")
async def ping():
    return JSONResponse({"result": "pong"})


@app.get(f"/{BOT_APPID}.json")
async def qq_url_check():
    return JSONResponse({"bot_appid": {BOT_APPID}})


from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/copy", response_class=HTMLResponse)
async def copy_page(content: str = ""):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>自动复制</title>
        <style>
            body {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: #f5f5f5;
                font-family: Arial, sans-serif;
            }}
            .success {{
                text-align: center;
                color: #333;
                font-size: 18px;
            }}
        </style>
    </head>
    <body>
        <div class="success">
            <h2>✅ 已自动复制到剪贴板</h2>
            <p>可以关闭此页面了</p>
        </div>

        <script>
            (async function() {{
                try {{
                    await navigator.clipboard.writeText("{content}");
                    setTimeout(() => window.close(), 800);
                }} catch (err) {{
                    document.body.innerHTML = '<div class="success"><h2>❌ 复制失败</h2><p>请手动复制</p></div>';
                }}
            }})();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

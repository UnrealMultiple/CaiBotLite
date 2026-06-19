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


@app.get("/copy", response_class=HTMLResponse)
async def copy_page(content: str = ""):
    # 转义特殊字符，防止 XSS
    import json
    content_json = json.dumps(content)  # 安全地序列化为 JS 字符串

    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>复制内容</title>
        <style>
            body {{
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                background: #f5f5f5;
                font-family: Arial, sans-serif;
            }}
            .card {{
                text-align: center;
                background: white;
                border-radius: 12px;
                padding: 32px 40px;
                box-shadow: 0 2px 12px rgba(0,0,0,0.1);
                max-width: 480px;
                width: 90%;
            }}
            .card h2 {{
                margin: 0 0 16px;
                color: #333;
                font-size: 20px;
            }}
            #copy-btn {{
                display: inline-block;
                margin-top: 8px;
                padding: 10px 28px;
                background: #4f46e5;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: background 0.2s;
            }}
            #copy-btn:hover {{ background: #4338ca; }}
            #copy-btn:active {{ background: #3730a3; }}
            #fallback {{
                display: none;
                margin-top: 16px;
                text-align: left;
            }}
            #fallback p {{
                margin: 0 0 6px;
                color: #555;
                font-size: 14px;
            }}
            #fallback textarea {{
                width: 100%;
                box-sizing: border-box;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                resize: vertical;
                min-height: 80px;
            }}
            #status {{
                margin-top: 12px;
                font-size: 14px;
                min-height: 20px;
                color: #16a34a;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>📋 复制内容</h2>
            <button id="copy-btn" onclick="doCopy()">点击复制</button>
            <div id="fallback">
                <p>浏览器不支持自动复制，请手动复制：</p>
                <textarea id="fallback-text" readonly></textarea>
            </div>
            <div id="status"></div>
        </div>

        <script>
            const content = {content_json};

            async function doCopy() {{
                try {{
                    await navigator.clipboard.writeText(content);
                    document.getElementById('status').textContent = '✅ 已复制到剪贴板';
                    document.getElementById('copy-btn').textContent = '✅ 已复制';
                    document.getElementById('copy-btn').style.background = '#16a34a';
                }} catch (err) {{
                    showFallback();
                }}
            }}

            function showFallback() {{
                document.getElementById('fallback').style.display = 'block';
                const ta = document.getElementById('fallback-text');
                ta.value = content;
                ta.select();
                document.getElementById('status').textContent = '⚠️ 请手动复制上方文本';
                document.getElementById('status').style.color = '#d97706';
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

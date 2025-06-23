import asyncio
import base64
import datetime
import io
import os
import uuid
import zipfile
from pathlib import Path

import nonebot
from fastapi import FastAPI, HTTPException
from starlette.responses import FileResponse

MAX_FILE_SIZE = 50 * 1024 * 1024
TEMP_UPLOAD_DIR = Path("temp")
TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
FILE_EXPIRATION = datetime.timedelta(minutes=30)
files_db = {}

app = nonebot.get_app()
app: FastAPI


@app.get("/download/{file_id}")
async def download_file(file_id: str):
    if file_id not in files_db:
        raise HTTPException(404, "File not found")

    file_info = files_db[file_id]

    if datetime.datetime.now() > file_info["expire_time"]:
        file_info["path"].unlink(missing_ok=True)
        del files_db[file_id]
        raise HTTPException(410, "Download link expired")

    return FileResponse(
        file_info["path"],
        filename=file_info["filename"]
    )


start_file_clear = nonebot.get_driver()


@start_file_clear.on_startup
async def start_file_clear_function():
    asyncio.create_task(file_cleanup_task())


async def file_cleanup_task():
    for filename in os.listdir(TEMP_UPLOAD_DIR):
        file_path = os.path.join(TEMP_UPLOAD_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except:
            pass
    while True:
        await asyncio.sleep(60)
        now = datetime.datetime.now()
        to_remove = [file_id for file_id, info in files_db.items() if now > info["expire_time"]]

        for file_id in to_remove:
            info = files_db.pop(file_id, None)
            if info and info["path"].exists():
                info["path"].unlink()

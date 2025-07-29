from pathlib import Path

import nonebot
from fastapi import FastAPI, HTTPException
from starlette.responses import FileResponse

from caibotlite.services.file import FileService

app = nonebot.get_app()
app: FastAPI


@app.get("/download/{file_id}")
async def download_file(file_id: str):
    if file_id not in FileService.files_db:
        raise HTTPException(404, "没有找到文件, 可能是文件过期了呢~")

    file_info = FileService.files_db[file_id]

    return FileResponse(
        file_info["path"],
        filename=file_info["filename"]
    )


@app.get("/plugin/{name}")
async def download_file(name: str):
    try:
        if name.find("/") != -1:
            raise HTTPException(403, detail="无效插件名!")

        full_path = Path("./plugins") / name
        full_path = full_path.resolve()

        # 检查文件是否存在
        if not full_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")

        # 返回文件
        return FileResponse(
            path=full_path,
            filename=full_path.name,
            media_type='application/octet-stream',
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

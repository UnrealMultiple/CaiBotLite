from pathlib import Path

import nonebot
from fastapi import FastAPI, HTTPException
from starlette.responses import FileResponse

from caibotlite.models import FileInfo
from caibotlite.services.file import FileService

app = nonebot.get_app()
app: FastAPI

IMAGES_DIR = Path(__file__).resolve().parents[2] / "assets" / "images"
ICON_DIR = IMAGES_DIR / "icons"

# category -> (subfolder, filename_template)
CATEGORY_DIR_MAP = {
    "item":       ("items",       "Item_{}.png"),
    "npc":        ("npcs",        "NPC_{}.png"),
    "projectile": ("projectiles", "Projectile_{}.png"),
    "buff":       ("buffs",       "Buff_{}.png"),
}


@app.get("/download/{file_id}")
async def download_file(file_id: str):
    if file_id not in FileService.files_db:
        raise HTTPException(404, "没有找到文件, 可能是文件过期了呢~")

    file_info: FileInfo = FileService.files_db[file_id]

    return FileResponse(
        file_info.path,
        filename=file_info.filename
    )


@app.get("/plugin/{name}")
async def download_file(name: str):
    try:
        if name.find("/") != -1:
            raise HTTPException(403, detail="找不到这个插件捏~")

        full_path = Path("./plugins") / name
        full_path = full_path.resolve()

        # 检查文件是否存在
        if not full_path.is_file():
            raise HTTPException(status_code=404, detail="找不到文件喵~")

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


@app.get("/image/{category}/{item_id}")
async def get_resource_image(category: str, item_id: int):
    """Serve terraria resource images by category and numeric ID.
    category: item | npc | projectile | buff
    """
    try:
        if category not in CATEGORY_DIR_MAP:
            raise HTTPException(status_code=404, detail="未知的资源类型")
        folder, template = CATEGORY_DIR_MAP[category]
        filename = template.format(item_id)
        full_path = (IMAGES_DIR / folder / filename).resolve()
        base_dir = (IMAGES_DIR / folder).resolve()
        if full_path.parent != base_dir:
            raise HTTPException(status_code=403, detail="找不到这张图片捏~")
        if not full_path.is_file():
            raise HTTPException(status_code=404, detail="找不到这张图片喵~")
        return FileResponse(path=full_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/image/{name}")
async def get_icon_image(name: str):
    try:
        requested_path = Path(name)
        if requested_path.name != name or requested_path.is_absolute():
            raise HTTPException(status_code=403, detail="找不到这张图片捏~")

        full_path = (ICON_DIR / requested_path).resolve()

        if full_path.parent != ICON_DIR.resolve():
            raise HTTPException(status_code=403, detail="找不到这张图片捏~")

        if not full_path.is_file():
            raise HTTPException(status_code=404, detail="找不到这张图片喵~")

        return FileResponse(path=full_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


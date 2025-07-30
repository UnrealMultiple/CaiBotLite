import base64
import io
import shutil
import uuid
import zipfile
from pathlib import Path
from typing import Optional

from expiringdict import ExpiringDict

from caibotlite.constants import FileSystem
from caibotlite.models.file_info import FileInfo


class FileService:
    TEMP_UPLOAD_DIR = Path("./temp")
    files_db: ExpiringDict[int, FileInfo] = ExpiringDict(max_len=100, max_age_seconds=FileSystem.FILE_EXPIRATION)

    @classmethod
    async def validate_zip_content(cls, file_bytes: bytes):
        # noinspection PyBroadException
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as zip_file:
                for name in zip_file.namelist():
                    if not name.lower().endswith(('.wld', '.twld', '.plr', '.tplr', '.map', '.tmap')):
                        return False
                return True
        except:
            return False

    @classmethod
    async def create_upload_link(cls, file_data: str, file_name: str, server_token: Optional[str] = None):
        file_bytes = base64.b64decode(file_data)
        if not file_name.lower().endswith(('.wld', '.twld', '.plr', '.tplr', '.map', '.tmap', '.zip')):
            return {
                "success": False,
                "message": "无效文件名"
            }

        if len(file_bytes) > FileSystem.MAX_FILE_SIZE_MB * 1024 * 1024:
            return {
                "success": False,
                "message": f"文件大小不能超过{FileSystem.MAX_FILE_SIZE_MB}MB"
            }

        file_id = uuid.uuid4().hex
        temp_path = cls.TEMP_UPLOAD_DIR / file_id

        if file_name.lower().endswith('.zip'):
            if not await cls.validate_zip_content(file_bytes):
                temp_path.unlink(missing_ok=True)
                return {
                    "success": False,
                    "message": "压缩包内含有无效文件名"
                }

        # noinspection PyBroadException
        try:
            with open(temp_path, "wb") as f:
                f.write(file_bytes)
        except:
            return {
                "success": False,
                "message": "文件写入失败"
            }
        cls.files_db[file_id] = FileInfo(temp_path, file_name, server_token)

        return {
            "success": True,
            "message": "OK",
            "download_url": f"/download/{file_id}",
            "original_filename": file_name
        }

    @classmethod
    def clean_all_temps(cls):
        cls.files_db.clear()
        temp_dir = Path(cls.TEMP_UPLOAD_DIR)
        if temp_dir.exists() and temp_dir.is_dir():
            for item in temp_dir.iterdir():
                # noinspection PyBroadException
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception:
                    continue


FileService.TEMP_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
FileService.clean_all_temps()

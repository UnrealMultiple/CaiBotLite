from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FileInfo:
    path: Path
    filename: str
    source_server_token: Optional[str]

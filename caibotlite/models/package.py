from typing import Dict, Any, Optional

from pydantic import BaseModel

from caibotlite.enums.package_direction import PackageDirection
from caibotlite.enums.package_type import PackageType


class Package(BaseModel):
    version: str
    direction: PackageDirection
    type: PackageType
    is_request: bool
    request_id: Optional[str]
    payload: Dict[str, Any]

    class Config:
        arbitrary_types_allowed = True

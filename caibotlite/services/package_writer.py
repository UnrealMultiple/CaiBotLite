import uuid
from typing import Any

from caibotlite.enums.package_direction import PackageDirection
from caibotlite.enums.package_type import PackageType
from caibotlite.models.package import Package


class PackageWriter:
    def __init__(self, package_type: PackageType, is_request: bool = True):
        self.package = Package(
            version=package_type.get_version(),
            direction=PackageDirection.TO_SERVER,
            type=package_type,
            is_request=is_request,
            request_id=None,
            payload={})

    def write(self, key: str, value: Any):
        self.package.payload[key] = value

    def build(self):
        if self.package.is_request:
            self.package.request_id = uuid.uuid4().hex
        return self.package

from typing import Optional

from geoip2.database import Reader


class GeoIP:
    reader: Reader

    @classmethod
    def init(cls):
        cls.reader = Reader(r'./data/GeoLite2-City.mmdb')

    @classmethod
    def get_city(cls, ip: str) -> Optional[str]:
        # noinspection PyBroadException
        try:
            city = cls.reader.city(ip).city.names
        except Exception:
            return None

        if not city:
            return None

        return city['zh-CN']


if __name__ == "__main__":
    GeoIP.init()
    print(GeoIP.get_city("112.48.151.0"))

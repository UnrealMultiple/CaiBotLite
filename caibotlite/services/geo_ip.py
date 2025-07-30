from typing import Optional

from geoip2.database import Reader


class GeoIP:
    reader: Reader

    @classmethod
    def init(cls):
        cls.reader = Reader(r'./data/GeoCN.mmdb')

    @classmethod
    def get_city(cls, ip: str) -> Optional[str]:
        # noinspection PyBroadException
        ip_info = cls.reader._db_reader.get(ip)
        if ip_info is None:
            return None

        if "city" in ip_info and ip_info['city']:
            return ip_info['city']

        if "province" in ip_info and ip_info['province']:
            return ip_info['province']

        return None


if __name__ == "__main__":
    GeoIP.init()
    print(GeoIP.get_city("112.47.150.63"))

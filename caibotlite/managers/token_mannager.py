from dataclasses import dataclass
from typing import Optional

from expiringdict import ExpiringDict


@dataclass
class TokenInfo:
    token: str
    group_open_id: str


class TokenManager:
    cache_tokens: ExpiringDict[int, TokenInfo] = ExpiringDict(max_len=100, max_age_seconds=120)

    @classmethod
    def try_get_token(cls, verification_code: int) -> Optional[TokenInfo]:
        if verification_code not in cls.cache_tokens:
            return None

        return cls.cache_tokens[verification_code]

    @classmethod
    def set_token(cls, group_open_id: str, verification_code: int, token: str):
        cls.cache_tokens[verification_code] = TokenInfo(token, group_open_id)

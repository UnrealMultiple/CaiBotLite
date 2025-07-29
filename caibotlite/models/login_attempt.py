from dataclasses import dataclass


@dataclass
class LoginAttempt:
    user_open_id: str
    login_uuid: str
    login_ip: str
    login_city: str
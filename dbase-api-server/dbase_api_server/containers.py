from dataclasses import dataclass


@dataclass
class DBaseConnection:
    user: str
    password: str
    host: str
    port: int
    database: str

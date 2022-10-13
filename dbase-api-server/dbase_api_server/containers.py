from dataclasses import dataclass


@dataclass
class ConnectionParams:
    host: str
    port: int
    user: str
    password: str
    database: str

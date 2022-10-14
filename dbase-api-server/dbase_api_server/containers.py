from dataclasses import dataclass
from typing import List


@dataclass
class ConnectionParams:
    host: str
    port: int
    user: str
    password: str
    database: str

    @property
    def docker_env(self) -> List[str]:
        return [
            f'POSTGRES_USER={self.user}',
            f'POSTGRES_PASSWORD={self.password}',
            f'POSTGRES_DB={self.database}'
        ]

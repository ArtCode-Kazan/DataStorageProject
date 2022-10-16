"""Module with common containers (dataclasses).

This module organize information about objects.

"""

from dataclasses import dataclass
from typing import List

__all__ = ['PostgresConnectionParams']


@dataclass
class PostgresConnectionParams:
    """Container with connection parameters for Postgres access.

    Args:
        host: host address
        port: port number
        user: username in Postgres
        password: user password
        database: Postgres database name

    """

    host: str
    port: int
    user: str
    password: str
    database: str

    @property
    def docker_env(self) -> List[str]:
        """Return list object with environment variables for docker client.

        Returns: list of environment variables

        """
        return [
            f'POSTGRES_USER={self.user}',
            f'POSTGRES_PASSWORD={self.password}',
            f'POSTGRES_DB={self.database}'
        ]

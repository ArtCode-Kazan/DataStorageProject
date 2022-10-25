"""Module with common containers (dataclasses).

This module organize information about objects.

"""

from dataclasses import dataclass
from typing import List

__all__ = ['PostgresConnectionParams', 'ResponseContainer']


@dataclass
class PostgresConnectionParams:
    """Container with connection parameters for Postgres access.

    Args:
        host: host address
        port: port number
        user: username in Postgres
        password: user password
        dbname: Postgres database name

    """

    host: str
    port: int
    user: str
    password: str
    dbname: str

    @property
    def docker_env(self) -> List[str]:
        """Return list object with environment variables for docker client.

        Returns: list of environment variables

        """
        return [
            f'POSTGRES_USER={self.user}',
            f'POSTGRES_PASSWORD={self.password}',
            f'POSTGRES_DB={self.dbname}'
        ]

    @property
    def connection_string(self) -> str:
        """Return connection line for psycopg.

        Returns: connection string

        """
        return (f'host={self.host} port={self.port} '
                f'user={self.user} password={self.password} '
                f'dbname={self.dbname}')


@dataclass
class ResponseContainer:
    """Container with API response dictionary.

    Args:
        status: response status
        message: description with response action
        data: info about deposit area name

    """
    status: bool
    message: str
    data: dict

    def convert_to_dict(self) -> dict:
        """Returns API response dictionary.

        Returns: response dict

        """
        return {
            'status': self.status,
            'message': self.message,
            'data': self.data
        }

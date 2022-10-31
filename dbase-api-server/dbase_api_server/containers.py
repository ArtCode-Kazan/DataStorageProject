"""Module with common containers (dataclasses).

This module organize information about objects.

"""

from dataclasses import dataclass
from typing import List, Union

from pydantic import BaseModel

__all__ = [
    'PostgresConnectionParams',
    'UvicornConnectionParams',
    'ResponseContainer'
]


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
class UvicornConnectionParams:
    """Container with connection parameters for uvicorn.

    Args:
        host: host address
        port: port number

    """
    host: str
    port: int

    @property
    def url_address(self) -> str:
        """Return full url address.

        Returns: string with url address

        """
        return f'http://{self.host}:{self.port}'


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
    data: Union[dict, list, int, float, str]

    def convert_to_dict(self) -> dict:
        """Returns API response dictionary.

        Returns: response dict

        """
        return {
            'status': self.status,
            'message': self.message,
            'data': self.data
        }


@dataclass
class Deposits(BaseModel):
    """Model with field for adding new deposit.

    Args:
        area_name: deposit name for adding

    """
    area_name: str


@dataclass
class UpdateDeposits(BaseModel):
    """Model with fields for renaming deposit area name.

    Args:
        old_area_name: initial area name
        new_area_name: area name for renaming

    """
    old_area_name: str
    new_area_name: str

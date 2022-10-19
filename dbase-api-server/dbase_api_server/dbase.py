"""Module for working with microservice Postgres database.

The module contains wrapper class around Postgres database for saving
storage metadata.

Examples:
    Adapter initialization::
        from dbase_api_server.containers import PostgresConnectionParams
        from environment import StorageDBase

        connection_params = PostgresConnectionParams(
            host='127.0.0.1',
            port=5432,
            user='user-1',
            password='qwerty',
            database='simple-dbase'
        )
        my_adapter = StorageDBase(params=connection_params)

"""

import logging

from psycopg2 import (DatabaseError, DataError, InternalError,
                      OperationalError, ProgrammingError)
from psycopg2 import connect as connect_to_db
from psycopg2._psycopg import connection as postgres_connection
from psycopg2.errors import UniqueViolation

from dbase_api_server.containers import PostgresConnectionParams

DEFAULT_PORT = 5432
DEFAULT_PATH = '/var/lib/postgresql/data'


class StorageDBase:
    """Database adapter for saving storage metadata."""

    def __init__(self, params: PostgresConnectionParams):
        """Initialize class method.

        Args:
            params: container with connection parameters (host, port, etc.)
        """
        self.__connection = connect_to_db(
            host=params.host,
            port=params.port,
            user=params.user,
            password=params.password,
            database=params.database
        )
        self.cursor = self.__connection.cursor()

    @property
    def connection(self) -> postgres_connection:
        """Return postgres connection object.

        Returns: connection object from psycopg2

        """
        return self.__connection

    def commit(self) -> bool:
        """Commit changes in database.

        If commit unsuccessful - create message in logger

        Returns: True if commit is success, False - if commit  has some error.

        """
        try:
            self.__connection.commit()
            return True
        except OperationalError as error:
            logging.error(error, 'problems with database operation')
        except DataError as error:
            logging.error(error, 'problems with processed data')
        except InternalError as error:
            logging.error(error, 'database encounters an internal error')
        except ProgrammingError as error:
            logging.error(error, 'wrong number of parameters')
        except DatabaseError as error:
            logging.error(error, 'problems with database')
        return False

    def add_deposit_info(self, area_name: str) -> bool:
        """Add deposit info to database.

        Args:
            area_name: deposit area name

        Returns: True if info was added success, False - if not.

        """
        insert_query = """
            INSERT INTO deposits(area_name)
            VALUES(%s);
        """
        try:
            self.cursor.execute(insert_query, (area_name,))
            return self.commit()
        except UniqueViolation as error:
            logging.error(error, 'column name already exists')

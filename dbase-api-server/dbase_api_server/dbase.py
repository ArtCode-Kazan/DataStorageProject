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
            dbname='simple-dbase'
        )
        my_adapter = StorageDBase(params=connection_params)

"""

import logging
from typing import List, Union

from psycopg import OperationalError, connect
from psycopg.connection import Connection
from psycopg.errors import CheckViolation, UniqueViolation
from pypika import Query, Table

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
        try:
            self.__connection = connect(conninfo=params.connection_string)
        except OperationalError:
            logging.error('problems with database operation')
            raise

    @property
    def connection(self) -> Connection:
        """Return postgres connection object.

        Returns: connection object from psycopg2

        """
        return self.__connection

    def select_one_record(self, query: str) -> Union[None, str, int, float,
                                                     tuple]:
        """Select only one record.

        Args:
            query: string with query text

        Returns: value of record. If no record return None

        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        record = cursor.fetchone()
        if record is None:
            return
        return record[0]

    def select_many_records(self, query: str) -> Union[None, list]:
        """Return many selected records.

        Args:
            query: string with query text

        Returns: list of selected rows. If no records - return None

        """
        cursor = self.connection.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        if records is None:
            return
        return records

    def is_success_changing_query(self, query: str) -> bool:
        """Return changing query status.

        Args:
            query: string with query text

        Returns: True - if success, else - False

        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            return True
        except UniqueViolation:
            logging.error('field(s) has non unique value')
        except CheckViolation:
            logging.error('field(s) dont pass dbase check condition(s)')

        self.connection.rollback()
        return False

    def add_deposit_info(self, area_name: str) -> bool:
        """Add deposit info to database.

        Args:
            area_name: deposit area name

        Returns: True if info was added success, False - if not.

        """
        lower_area_name = area_name.lower()

        table = Table('deposits')
        query = str(
            Query.into(table).columns('area_name').insert(lower_area_name)
        )
        return self.is_success_changing_query(query=query)

    def get_all_deposit_names(self) -> List[str]:
        """Get all deposit info from database.

        Returns: True if query completed succes, False - if not
        """
        table = Table('deposits')
        query = str(Query.from_(table).select('area_name'))
        return self.select_many_records(query=query)

import logging

from psycopg2._psycopg import connection
from psycopg2 import connect
from psycopg2 import OperationalError, DataError, InternalError
from psycopg2 import ProgrammingError, DatabaseError

from containers import ConnectionParams


class StorageDBase:
    def __init__(self, params: ConnectionParams):
        self.__connection = connect(
            host=params.host,
            port=params.port,
            user=params.user,
            password=params.password,
            database=params.database
        )
        self.cursor = self.__connection.cursor()

    @property
    def connection(self) -> connection:
        return self.__connection

    def __commit(self) -> bool:
        """Save changes ahter query and show errors"""
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

    def add_deposit_info(self,
                         area_name: str) -> bool:
        """Insert deposit data in 'deposits' table."""
        insert_query = """
            INSERT INTO deposits(area_name)
            VALUES(%s);
        """
        self.cursor.execute(insert_query, (area_name,))
        return self.__commit()

from dataclasses import dataclass
import logging

from psycopg2 import connect, connection

from psycopg2 import OperationalError, DataError, InternalError
from psycopg2 import ProgrammingError, DatabaseError


@dataclass
class DBaseConnection:
    user: str
    password: str
    host: str
    port: int
    database: str


class StorageDBase:
    def __init__(self, params: DBaseConnection):
        self.__connection = connect(
            user=params.user,
            password=params.password,
            host=params.host,
            port=params.port,
            database=params.database)
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

from dataclasses import dataclass
import logging

import psycopg2
from psycopg2 import OperationalError, DataError, InternalError
from psycopg2 import ProgrammingError, DatabaseError

from psycopg2 import connection


@dataclass
class DepositsDatabase:
    user: str
    password: str
    host: str
    port: int
    database: str

    def __post_init__(self):
        self.__connection = psycopg2.connect(
            host=self.host, port=self.port, database=self.database,
            user=self.user, password=self.password
        )
        self.cursor = self.__connection.cursor()

    @property
    def connection(self) -> connection:
        return self.__connection

    def __commit_db_changes(self) -> bool:
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
        return self.__commit_db_changes()

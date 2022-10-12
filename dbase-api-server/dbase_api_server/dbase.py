import psycopg2
from psycopg2 import connection, OperationalError, DataError
from psycopg2 import InternalError, ProgrammingError, DatabaseError


class DepositsDatabase:
    def __init__(self,
                 user: str,
                 password: str,
                 host: str,
                 port: int,
                 database: str
                 ):
        self.__connection = psycopg2.connect(
            host=host, port=port, database=database,
            user=user, password=password
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
            print(f'{error}: problems with database operation')
        except DataError as error:
            print(f'{error}: problems with processed data')
        except InternalError as error:
            print(f'{error}: database encounters an internal error')
        except ProgrammingError as error:
            print(f'{error}: wrong number of parameters')
        except DatabaseError as error:
            print(f'{error}: problems with database')
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

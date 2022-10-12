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

    def insert_deposit_data(self, area_name: str) -> bool:
        """Insert deposit data in 'deposits' table."""
        cursor = self.connection.cursor()
        insert_query = """
            INSERT INTO deposits(area_name)
            VALUES(%s);
        """
        cursor.execute(insert_query, (area_name,))

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

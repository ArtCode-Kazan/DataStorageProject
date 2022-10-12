import psycopg2
from psycopg2 import connection


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

    @property
    def connection(self) -> connection:
        return self.__connection

    @connection.setter
    def connection(self, new_value: connection) -> connection:
        self.__connection = new_value

    def add_deposit_info(self,
                         area_name: str) -> bool:
        """Insert deposit data in 'deposits' table."""
        cursor = self.__connection.cursor()
        query = """
            INSERT INTO deposits(area_name)
            VALUES(%s);
        """
        cursor.execute(query, (area_name,))

        try:
            self.__connection.commit()
            return True
        except psycopg2.OperationalError as error:
            return print(f'{error}: problems with database operation')
        except psycopg2.DataError as error:
            return print(f'{error}: problems with processed data')
        except psycopg2.InternalError as error:
            return print(f'{error}: database encounters an internal error')
        except psycopg2.ProgrammingError as error:
            return print(f'{error}: wrong number of parameters')
        except psycopg2.DatabaseError as error:
            return print(f'{error}: problems with database')

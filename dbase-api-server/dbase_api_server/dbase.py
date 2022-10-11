import psycopg2
from psycopg2 import Error, connection


class DepositsDatabase:
    def __init__(self,
                 user: str,
                 password: str,
                 host: str,
                 port: int,
                 database: str
                 ) -> None:
        self.__connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )

    @property
    def connection_params(self) -> connection:
        return self.__connection

    @connection_params.setter
    def connection_value_setup(self, new_value: connection) -> connection:
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
        except (Exception, Error):
            return False

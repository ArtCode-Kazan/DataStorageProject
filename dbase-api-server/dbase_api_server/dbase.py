import psycopg2
from psycopg2 import Error


class DepositsDatabase:
    def __init__(self,
                 user: str,
                 password: str,
                 host: str,
                 port: int,
                 database: str
                 ) -> None:
        self.connection = psycopg2.connect(user=user,
                                           password=password,
                                           host=host,
                                           port=port,
                                           database=database)

    def insert_deposit_data(self,
                            area_name: str) -> bool:
        """Insert deposit data in 'deposits' table."""
        cursor = self.connection.cursor()
        insert_query = """
            INSERT INTO deposits(area_name)
            VALUES(%s);
        """
        cursor.execute(insert_query, (area_name,))

        try:
            self.connection.commit()
            return True
        except (Exception, Error):
            return False

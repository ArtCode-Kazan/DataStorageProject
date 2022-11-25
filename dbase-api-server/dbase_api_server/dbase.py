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
from datetime import datetime
from typing import Union

from psycopg import OperationalError
from psycopg.connection import Connection
from psycopg.errors import (CheckViolation, StringDataRightTruncation,
                            UniqueViolation)
from pypika import Query, Table

from dbase_api_server.containers import PostgresConnectionParams
from dbase_api_server.models import DATETIME_FORMAT, StationInfo, WorkInfo

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
            self.__connection = Connection.connect(
                conninfo=params.connection_string
            )
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
        cursor.execute(query=query)
        record = cursor.fetchone()
        if record is None:
            return
        if len(record) == 1:
            return record[0]
        return record

    def select_many_records(self, query: str) -> Union[None, list]:
        """Return many selected records.

        Args:
            query: string with query text

        Returns: list of selected rows. If no records - return None

        """
        cursor = self.connection.cursor()
        cursor.execute(query=query)
        records = cursor.fetchall()
        if not records:
            return

        if len(records[0]) == 1:
            return [x[0] for x in records]
        return records

    def is_success_changing_query(self, query: str) -> bool:
        """Return changing query status.

        Args:
            query: string with query text

        Returns: True - if success, else - False

        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query=query)
            self.connection.commit()
            return True
        except UniqueViolation:
            logging.error('field(s) has non unique value')
        except CheckViolation:
            logging.error('field(s) dont pass dbase check condition(s)')
        except StringDataRightTruncation:
            logging.error('field(s) longer than allowed')

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

    def get_all_deposit_names(self) -> Union[None, list]:
        """Get all deposit info from database.

        Returns: True if query completed success, False - if not.
        """
        table = Table('deposits')
        query = str(Query.from_(table).select('area_name'))
        return self.select_many_records(query=query)

    def update_deposit_name(self, old_area_name: str,
                            new_area_name: str) -> bool:
        """Update deposit name.

        Args:
            old_area_name: deposit area name
            new_area_name: updated deposit area name

        Returns: True if name updated success, False - if not.
        """
        old_area_name = old_area_name.lower()
        new_area_name = new_area_name.lower()

        table = Table('deposits')
        query = str(
            Query.update(table).set(
                table.area_name, new_area_name).where(
                table.area_name == old_area_name
            )
        )
        return self.is_success_changing_query(query=query)

    def add_work_info(self, work_info: WorkInfo) -> bool:
        """Add works info to database.

        Args:
            work_info: container with works params

        """
        lower_well_name = work_info.well_name.lower()
        lower_work_type = work_info.work_type.lower()
        datetime_value = datetime.strptime(
            work_info.datetime_start_str,
            DATETIME_FORMAT
        )
        table = Table('works')
        query = str(
            Query.into(table).columns(
                'well_name', 'start_time', 'work_type', 'deposit_id').insert(
                lower_well_name, datetime_value,
                lower_work_type, work_info.deposit_id
            )
        )
        return self.is_success_changing_query(query=query)

    def update_work_info(self, old_work_info: WorkInfo,
                         new_work_info: WorkInfo) -> bool:
        """Method for updating works info.

        Args:
            old_work_info: container with parameters
            new_work_info: container with updated params

        Returns: True if name updated success, False - if not.

        """
        well_name = old_work_info.well_name.lower()
        updated_well_name = new_work_info.well_name.lower()
        work_type = old_work_info.work_type.lower()
        updated_work_type = new_work_info.work_type.lower()
        query = f"""UPDATE works SET well_name = '{updated_well_name}',
                    start_time = '{new_work_info.datetime_start_str}',
                    work_type = '{updated_work_type}',
                    deposit_id = '{new_work_info.deposit_id}'
                    WHERE well_name = '{well_name}'
                    AND start_time = '{old_work_info.datetime_start_str}'
                    AND work_type = '{work_type}'
                    AND deposit_id = '{old_work_info.deposit_id}'
        """
        return self.is_success_changing_query(query=query)

    def add_station_info(self, station_info: StationInfo) -> bool:
        """Add station info to database.

        Args:
            station_info: container with station params

        Returns: True if info was added success, False - if not.
        """
        table = Table('stations')
        query = str(
            Query.into(table).columns(
                'station_number', 'x_wgs84', 'y_wgs84', 'altitude', 'work_id'
            ).insert(
                station_info.station_number, station_info.x_wgs84,
                station_info.y_wgs84, station_info.altitude,
                station_info.work_id
            )
        )
        return self.is_success_changing_query(query=query)

    def update_station_info(self, old_station_info: StationInfo,
                            new_station_info: StationInfo) -> bool:
        """Method for updating station info.

        Args:
            old_station_info: container with parameters
            new_station_info: container with updated params

        Returns: True if name updated success, False - if not.

        """
        query = f"""UPDATE stations SET
        station_number = {new_station_info.station_number},
        x_wgs84 = {new_station_info.x_wgs84},
        y_wgs84 = {new_station_info.y_wgs84},
        altitude = {new_station_info.altitude},
        work_id = {new_station_info.work_id}
        WHERE station_number = {old_station_info.station_number}
        AND x_wgs84 = {old_station_info.x_wgs84}
        AND y_wgs84 = {old_station_info.y_wgs84}
        AND altitude = {old_station_info.altitude}
        AND work_id = {old_station_info.work_id}
        """
        return self.is_success_changing_query(query=query)

    def get_stations_info(self, work_id: str) -> Union[None, list]:
        """Get station info by well name.

        Args:
            work_id: associated with station id

        Returns: list of selected rows. If no records - return None.
        """
        table = Table('stations')
        query = str(
            Query.from_(table).select(
                'station_number', 'x_wgs84', 'y_wgs84', 'altitude',
                'work_id').where(table.work_id == work_id)
        )
        records = self.select_many_records(query=query)
        station_list = []
        for record in records:
            station_info = StationInfo(
                station_number=record[0],
                x_wgs84=record[1],
                y_wgs84=record[2],
                altitude=record[3],
                work_id=record[4]
            )
            station_list += station_info
        return station_list

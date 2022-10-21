from unittest.mock import Mock, patch

from hamcrest import assert_that, equal_to, is_
from psycopg import OperationalError
from psycopg.connection import Connection
from pypika import Query, Table
from pypika.functions import Count

from dbase_api_server.containers import PostgresConnectionParams
from dbase_api_server.dbase import StorageDBase


class TestStorageDBase:
    connection_params = PostgresConnectionParams(
        host='some-host',
        port=7777,
        user='some-user',
        password='some-password',
        dbname='some-dbase'
    )

    @patch.object(Connection, '_wait_conn')
    def test_correct_init(self, wait_conn_mock: Mock):

        wait_conn_mock.return_value.prepare_threshold = None
        with patch.object(Connection, 'connect') as connect_mock:
            StorageDBase(params=self.connection_params)
            connect_mock.assert_called_once_with(
                conninfo=self.connection_params.connection_string
            )

    @patch('logging.error')
    @patch.object(Connection, '_wait_conn')
    def test_bad_init(self, wait_conn_mock: Mock, logging_mock: Mock):
        wait_conn_mock.return_value.prepare_threshold = None
        with patch.object(Connection, 'connect') as connect_mock:
            connect_mock.side_effect = OperationalError
            try:
                StorageDBase(params=self.connection_params)
                is_success = False
            except OperationalError:
                is_success = True

            assert_that(actual_or_assertion=is_success, matcher=is_(True))
            connect_mock.assert_called_once_with(
                conninfo=self.connection_params.connection_string
            )
            logging_mock.assert_called_once()

    def test_select_one_record(self, up_test_dbase):
        table = Table('deposits')

        query = str(Query.from_(table).select(Count(1)))
        records_count = up_test_dbase.select_one_record(query=query)
        assert_that(
            actual_or_assertion=records_count,
            matcher=equal_to(0)
        )

        query = str(
            Query.from_(table).select('area_name').where(table.area_name == '')
        )
        record = up_test_dbase.select_one_record(query=query)
        assert_that(
            actual_or_assertion=record,
            matcher=is_(None)
        )

    def test_select_many_records(self, up_test_dbase, fill_deposit_names):
        area_names_count = fill_deposit_names
        table = Table('deposits')

        query = str(Query.from_(table).select('*'))
        records = up_test_dbase.select_many_records(query=query)
        assert_that(
            actual_or_assertion=len(records),
            matcher=equal_to(area_names_count)
        )
        assert_that(actual_or_assertion=isinstance(records, list),
                    matcher=is_(True))

        query = str(
            Query.from_(table).select('area_name').where(table.area_name == '')
        )
        records = up_test_dbase.select_many_records(query=query)
        assert_that(
            actual_or_assertion=records,
            matcher=is_(None)
        )

    def test_add_deposit_name(self, up_test_dbase, clear_deposits_table):
        is_added = up_test_dbase.add_deposit_info('test-area')
        assert_that(actual_or_assertion=is_added, matcher=is_(True))

        table = Table('deposits')
        query = str(
            Query.from_(table).select(Count(1)).where(
                table.area_name == 'test-area'
            )
        )
        cursor = up_test_dbase.connection.cursor()
        cursor.execute(query)
        records_count = cursor.fetchone()[0]
        assert_that(actual_or_assertion=records_count, matcher=equal_to(1))

    def test_blank_deposit_name(self, up_test_dbase, clear_deposits_table):
        is_added = up_test_dbase.add_deposit_info('')
        assert_that(actual_or_assertion=is_added, matcher=is_(False))

        table = Table('deposits')
        query = str(
            Query.from_(table).select(Count(1)).where(
                table.area_name == ''
            )
        )
        cursor = up_test_dbase.connection.cursor()
        cursor.execute(query)
        records_count = cursor.fetchone()[0]
        assert_that(actual_or_assertion=records_count, matcher=equal_to(0))

    def test_duplicate_deposits_names(self, up_test_dbase,
                                      clear_deposits_table):
        is_added = up_test_dbase.add_deposit_info('test-area')
        assert_that(actual_or_assertion=is_added, matcher=is_(True))

        is_added = up_test_dbase.add_deposit_info('test-area')
        assert_that(actual_or_assertion=is_added, matcher=is_(False))

        table = Table('deposits')
        query = str(
            Query.from_(table).select(Count(1)).where(
                table.area_name == 'test-area'
            )
        )
        cursor = up_test_dbase.connection.cursor()
        cursor.execute(query)
        count = cursor.fetchone()[0]
        assert_that(actual_or_assertion=count, matcher=equal_to(1))

    def test_upper_and_lower_deposit_names(self, up_test_dbase,
                                           clear_deposits_table):
        is_added = up_test_dbase.add_deposit_info('test-area')
        assert_that(actual_or_assertion=is_added, matcher=is_(True))

        is_added = up_test_dbase.add_deposit_info('TEST-AREA')
        assert_that(actual_or_assertion=is_added, matcher=is_(False))

        table = Table('deposits')
        query = str(
            Query.from_(table).select(Count(1)).where(
                table.area_name == 'test-area'
            )
        )
        cursor = up_test_dbase.connection.cursor()
        cursor.execute(query)
        count = cursor.fetchone()[0]
        assert_that(actual_or_assertion=count, matcher=equal_to(1))

    def test_get_all_deposit_names(self, up_test_dbase,
                                   clear_deposits_table):
        area_names = ['test-name-1', 'test-name-2', 'test-name-3']
        for area_name in area_names:
            up_test_dbase.add_deposit_info(area_name=area_name)

        records = up_test_dbase.get_all_deposit_names()
        assert_that(
            actual_or_assertion=len(records),
            matcher=equal_to(len(area_names))
        )
        assert_that(actual_or_assertion=isinstance(records, list),
                    matcher=is_(True))
        assert_that(actual_or_assertion=records, matcher=area_names)

    def test_update_deposit_name(self, up_test_dbase,
                                 clear_deposits_table):
        old_area_name = 'test-name'
        is_added = up_test_dbase.add_deposit_info(old_area_name)
        assert_that(actual_or_assertion=is_added, matcher=is_(True))

        new_area_name = 'test-name-1'
        is_updated = up_test_dbase.update_deposit_name(old_area_name,
                                                       new_area_name)
        assert_that(actual_or_assertion=is_updated, matcher=is_(True))

        table = Table('deposits')
        query = str(
            Query.from_(table).select(Count(1)).where(
                table.area_name == 'test-name-1'
            )
        )
        count = up_test_dbase.select_one_record(query)
        assert_that(actual_or_assertion=count, matcher=equal_to(1))

    def test_update_blank_deposit_name(self, up_test_dbase,
                                       clear_deposits_table):
        old_area_name = 'test-name'
        is_added = up_test_dbase.add_deposit_info(old_area_name)
        assert_that(actual_or_assertion=is_added, matcher=is_(True))

        new_area_name = ''
        is_added = up_test_dbase.update_deposit_name(old_area_name,
                                                     new_area_name)
        assert_that(actual_or_assertion=is_added, matcher=is_(False))

    def test_update_duplicate_deposit_name(self, up_test_dbase,
                                           clear_deposits_table):
        old_area_name = 'test-name'
        is_added = up_test_dbase.add_deposit_info(old_area_name)
        assert_that(actual_or_assertion=is_added, matcher=is_(True))

        new_area_name = 'test-name'
        is_added = up_test_dbase.update_deposit_name(old_area_name,
                                                     new_area_name)
        assert_that(actual_or_assertion=is_added, matcher=is_(False))

    def test_update_missing_deposit_name(self, up_test_dbase,
                                         clear_deposits_table):
        old_name = 'test-name'
        new_area_name = 'test-name-1'
        up_test_dbase.update_deposit_name(old_name,
                                          new_area_name)

        table = Table('deposits')
        query = str(
            Query.from_(table).select(Count(1)).where(
                table.area_name == 'test-name-1'
            )
        )
        count = up_test_dbase.select_one_record(query)
        assert_that(actual_or_assertion=count, matcher=equal_to(0))

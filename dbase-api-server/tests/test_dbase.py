from unittest.mock import Mock, call, patch

import pytest
from hamcrest import assert_that, equal_to, is_
from psycopg import OperationalError
from psycopg.connection import Connection
from psycopg.errors import CheckViolation, UniqueViolation
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

    @patch.object(Connection, 'connect')
    @patch.object(Connection, '_wait_conn')
    def test_correct_init(self, wait_conn_mock: Mock, connect_mock: Mock):
        wait_conn_mock.return_value.prepare_threshold = None
        connect_mock.return_value = 'some-connect'

        dbase_obj = StorageDBase(params=self.connection_params)
        connect_mock.assert_called_once_with(
            conninfo=self.connection_params.connection_string
        )
        assert_that(
            actual_or_assertion=dbase_obj.connection,
            matcher=equal_to('some-connect')
        )

    @patch('logging.error')
    @patch.object(Connection, 'connect')
    @patch.object(Connection, '_wait_conn')
    def test_bad_init(self, wait_conn_mock: Mock, connect_mock: Mock,
                      logging_mock: Mock):
        wait_conn_mock.return_value.prepare_threshold = None
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

    @pytest.mark.parametrize(['fetch_values', 'expected_values'],
                             [(('some-value',), 'some-value'),
                              ((1, 2, 3, 4, 5), (1, 2, 3, 4, 5)),
                              (None, None)])
    @patch.object(Connection, 'connect')
    @patch.object(Connection, '_wait_conn')
    def test_select_one_record(self, wait_conn_mock: Mock, connect_mock: Mock,
                               fetch_values, expected_values):
        wait_conn_mock.return_value.prepare_threshold = None
        cursor_mock = Mock(
            execute=Mock(return_value=True),
            fetchone=Mock(return_value=fetch_values)
        )

        connect_mock.return_value = Mock(
            cursor=Mock(return_value=cursor_mock)
        )

        dbase_obj = StorageDBase(self.connection_params)
        record = dbase_obj.select_one_record(query='some-query')

        assert_that(
            actual_or_assertion=record,
            matcher=equal_to(expected_values)
        )

        connect_mock.assert_has_calls(calls=[call().cursor()])
        cursor_mock.execute.assert_called_once_with(query='some-query')
        cursor_mock.fetchone.assert_called_once()

    @pytest.mark.parametrize(
        ['fetch_values', 'expected_values'],
        [
            ([(1,), (2,), (3,)], [1, 2, 3]),
            ([(1, 2), (4, 5), (7, 8)], [(1, 2), (4, 5), (7, 8)]),
            (None, None)
        ]
    )
    @patch.object(Connection, 'connect')
    @patch.object(Connection, '_wait_conn')
    def test_select_many_records(self, wait_conn_mock: Mock,
                                 connect_mock: Mock,
                                 fetch_values, expected_values):
        wait_conn_mock.return_value.prepare_threshold = None
        cursor_mock = Mock(
            execute=Mock(return_value=True),
            fetchall=Mock(return_value=fetch_values)
        )

        connect_mock.return_value = Mock(
            cursor=Mock(return_value=cursor_mock)
        )

        dbase_obj = StorageDBase(self.connection_params)
        record = dbase_obj.select_many_records(query='some-query')

        assert_that(
            actual_or_assertion=record,
            matcher=equal_to(expected_values)
        )

        connect_mock.assert_has_calls(calls=[call().cursor()])
        cursor_mock.execute.assert_called_once_with(query='some-query')
        cursor_mock.fetchall.assert_called_once()

    @patch.object(Connection, 'connect')
    @patch.object(Connection, '_wait_conn')
    def test_is_success_changing_query_success(self, wait_conn_mock: Mock,
                                               connect_mock: Mock):
        wait_conn_mock.return_value.prepare_threshold = None
        cursor_mock = Mock(execute=Mock(return_value=True))

        connect_mock.return_value = Mock(
            cursor=Mock(return_value=cursor_mock),
            commit=Mock(return_value=True),
            rollback=Mock(return_value=True)
        )

        dbase_obj = StorageDBase(self.connection_params)
        is_success = dbase_obj.is_success_changing_query(query='some-query')

        is_rollback = call().rollback() in connect_mock.mock_calls
        connect_mock.assert_has_calls(calls=[call().cursor(), call().commit()])
        cursor_mock.execute.assert_called_once_with(query='some-query')
        assert_that(actual_or_assertion=is_rollback, matcher=is_(False))
        assert_that(actual_or_assertion=is_success, matcher=is_(True))

    @pytest.mark.parametrize('error_type', [UniqueViolation, CheckViolation])
    @patch('logging.error')
    @patch.object(Connection, 'connect')
    @patch.object(Connection, '_wait_conn')
    def test_is_success_changing_query_with_errors(self, wait_conn_mock: Mock,
                                                   connect_mock: Mock,
                                                   logging_mock: Mock,
                                                   error_type):
        wait_conn_mock.return_value.prepare_threshold = None
        cursor_mock = Mock(execute=Mock(side_effect=error_type))

        connect_mock.return_value = Mock(
            cursor=Mock(return_value=cursor_mock),
            commit=Mock(return_value=True),
            rollback=Mock(return_value=True)
        )

        dbase_obj = StorageDBase(self.connection_params)
        is_success = dbase_obj.is_success_changing_query(query='some-query')

        is_commit = call().commit() in connect_mock.mock_calls
        connect_mock.assert_has_calls(
            calls=[call().cursor(), call().rollback()]
        )
        cursor_mock.execute.assert_called_once_with(query='some-query')
        assert_that(actual_or_assertion=is_commit, matcher=is_(False))
        assert_that(actual_or_assertion=is_success, matcher=is_(False))
        logging_mock.assert_called_once()

    def test_add_deposit_name(self, up_test_dbase, clear_deposits_table):
        is_success = up_test_dbase.add_deposit_info('test-area')
        assert_that(actual_or_assertion=is_success, matcher=is_(True))

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
        is_success = up_test_dbase.add_deposit_info('')
        assert_that(actual_or_assertion=is_success, matcher=is_(False))

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
        is_success = up_test_dbase.add_deposit_info('test-area')
        assert_that(actual_or_assertion=is_success, matcher=is_(True))

        is_success = up_test_dbase.add_deposit_info('test-area')
        assert_that(actual_or_assertion=is_success, matcher=is_(False))

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
        is_success = up_test_dbase.add_deposit_info('test-area')
        assert_that(actual_or_assertion=is_success, matcher=is_(True))

        is_success = up_test_dbase.add_deposit_info('TEST-AREA')
        assert_that(actual_or_assertion=is_success, matcher=is_(False))

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
        assert_that(
            actual_or_assertion=isinstance(records, list),
            matcher=is_(True)
        )
        assert_that(
            actual_or_assertion=records,
            matcher=equal_to(area_names)
        )

    def test_update_deposit_name(self, up_test_dbase,
                                 clear_deposits_table):
        old_area_name = 'test-name'
        is_success = up_test_dbase.add_deposit_info(old_area_name)
        assert_that(actual_or_assertion=is_success, matcher=is_(True))

        new_area_name = 'test-name-1'
        is_success = up_test_dbase.update_deposit_name(
            old_area_name=old_area_name, new_area_name=new_area_name
        )
        assert_that(actual_or_assertion=is_success, matcher=is_(True))

        table = Table('deposits')
        query = str(
            Query.from_(table).select(Count(1)).where(
                table.area_name == new_area_name
            )
        )
        records_count = up_test_dbase.select_one_record(query)
        assert_that(actual_or_assertion=records_count, matcher=equal_to(1))

    def test_update_blank_deposit_name(self, up_test_dbase,
                                       clear_deposits_table):
        old_area_name = 'test-name'
        is_success = up_test_dbase.add_deposit_info(old_area_name)
        assert_that(actual_or_assertion=is_success, matcher=is_(True))

        new_area_name = ''
        is_success = up_test_dbase.update_deposit_name(
            old_area_name=old_area_name, new_area_name=new_area_name
        )
        assert_that(actual_or_assertion=is_success, matcher=is_(False))

        table = Table('deposits')
        query = str(
            Query.from_(table).select(Count(1)).where(
                table.area_name == old_area_name
            )
        )
        records_count = up_test_dbase.select_one_record(query)
        assert_that(actual_or_assertion=records_count, matcher=equal_to(1))

    def test_update_duplicate_deposit_name(self, up_test_dbase,
                                           clear_deposits_table):
        old_area_name = 'test-name'
        is_success = up_test_dbase.add_deposit_info(old_area_name)
        assert_that(actual_or_assertion=is_success, matcher=is_(True))

        new_area_name = 'test-name'
        is_success = up_test_dbase.update_deposit_name(old_area_name,
                                                       new_area_name)
        assert_that(actual_or_assertion=is_success, matcher=is_(True))

        table = Table('deposits')
        query = str(
            Query.from_(table).select(Count(1)).where(
                table.area_name == old_area_name
            )
        )
        records_count = up_test_dbase.select_one_record(query)
        assert_that(actual_or_assertion=records_count, matcher=equal_to(1))

    def test_update_missing_deposit_name(self, up_test_dbase,
                                         clear_deposits_table):
        old_area_name, new_area_name = 'test-name', 'test-name-1'
        is_success = up_test_dbase.update_deposit_name(
            old_area_name=old_area_name, new_area_name=new_area_name
        )
        assert_that(actual_or_assertion=is_success, matcher=is_(True))

        table = Table('deposits')
        query = str(
            Query.from_(table).select(Count(1)).where(
                table.area_name == new_area_name
            )
        )
        records_count = up_test_dbase.select_one_record(query)
        assert_that(actual_or_assertion=records_count, matcher=equal_to(0))

        table = Table('deposits')
        query = str(
            Query.from_(table).select(Count(1)).where(
                table.area_name == new_area_name
            )
        )
        records_count = up_test_dbase.select_one_record(query)
        assert_that(actual_or_assertion=records_count, matcher=equal_to(0))

    @pytest.mark.parametrize(
        ['passed_values', 'expected_values', 'expected_records_count'],
        [('a', True, 1), ('a' * 100, True, 1), ('a' * 111, False, 0)]
    )
    def test_field_deposit_name_lengh(self, up_test_dbase, passed_values,
                                      expected_values, expected_records_count):
        is_success = up_test_dbase.add_deposit_info(passed_values)
        assert_that(actual_or_assertion=is_success,
                    matcher=is_(expected_values))

        table = Table('deposits')
        query = str(
            Query.from_(table).select(Count(1)).where(
                table.area_name == passed_values
            )
        )
        is_added = up_test_dbase.select_one_record(query)
        assert_that(actual_or_assertion=is_added,
                    matcher=equal_to(expected_records_count))

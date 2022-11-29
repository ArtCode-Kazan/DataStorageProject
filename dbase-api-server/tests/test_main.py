import os

import requests
from dotenv import load_dotenv
from hamcrest import assert_that, equal_to
from pypika import Query, Table

from dbase_api_server.models import Deposit, StationInfo, WorkInfo

load_dotenv()

APP_HOST = os.getenv('APP_HOST')
APP_PORT = os.getenv('APP_PORT')
URL = f'http://{APP_HOST}:{APP_PORT}'


def test_get_all_deposits(up_test_dbase, clear_deposits_table):
    url = f'{URL}/get-all-deposits'
    response = requests.get(url)
    expected_value = {
        'status': True,
        'message': 'All deposits name returns successfully',
        'data': {
            'area_names': []
        }
    }
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )

    area_name = 'test-area'
    up_test_dbase.add_deposit_info(area_name=area_name)

    response = requests.get(url)
    expected_value = {
        'status': True,
        'message': 'All deposits name returns successfully',
        'data': {
            'area_names': [area_name]
        }
    }

    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )


def test_add_new_deposit(clear_deposits_table):
    url = f'{URL}/add-deposit'
    payload = Deposit(area_name='area-name')
    response = requests.post(url, json=payload.dict())
    expected_value = {
        'status': True,
        'message': f'Deposit name "{payload.area_name}" added successfully',
        'data': {}
    }
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )

    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )

    payload = Deposit(area_name='')
    expected_value = {
        'status': False,
        'message': f'Cant add deposit name "{payload.area_name}"',
        'data': {}
    }
    url = f'{URL}/add-deposit'
    response = requests.post(url, json=payload.dict())
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )


def test_update_deposit(up_test_dbase, clear_deposits_table):
    old_area_name, new_area_name = 'test-name', 'test-name-2'

    up_test_dbase.add_deposit_info(area_name=old_area_name)

    new_deposit = Deposit(
        area_name=new_area_name
    )
    old_deposit = Deposit(
        area_name=old_area_name
    )
    payload = {
        'old_deposit': old_deposit.dict(),
        'new_deposit': new_deposit.dict()
    }

    expected_value = {
        'status': True,
        'message': (f'Deposit "{old_area_name}" successfully '
                    f'renamed to "{new_area_name}"'),
        'data': {}
    }
    url = (f'{URL}/update-deposit')
    response = requests.post(url, json=payload)

    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )


def test_update_blank_deposit_name(up_test_dbase, clear_deposits_table):
    old_area_name, new_area_name = 'new_area_name', ''

    up_test_dbase.add_deposit_info(area_name=old_area_name)

    new_deposit = Deposit(
        area_name=new_area_name
    )
    old_deposit = Deposit(
        area_name=old_area_name
    )
    payload = {
        'old_deposit': old_deposit.dict(),
        'new_deposit': new_deposit.dict()
    }

    expected_value = {
        'status': False,
        'message': (f'Cant rename "{old_area_name} '
                    f'to "{new_area_name}"'),
        'data': {}
    }
    url = (f'{URL}/update-deposit')
    response = requests.post(url, json=payload)

    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )


def test_add_new_work(up_test_dbase, clear_deposits_table):
    up_test_dbase.add_deposit_info(area_name='test-area')

    table = Table('deposits')
    query = str(
        Query.from_(table).select('id').where(
            table.area_name == 'test-area'
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    area_id = cursor.fetchone()[0]

    url = f'{URL}/add-work-info'
    payload = WorkInfo(
        well_name='test-name',
        datetime_start_str='2022-11-15 12:12:12',
        work_type='test-work',
        deposit_id=area_id
    )
    expected_value = {
        'status': True,
        'message': (f'Successfully added work info: {payload.well_name}, '
                    f'{payload.datetime_start_str}, {payload.work_type}, '
                    f'{payload.deposit_id}'),
        'data': {}
    }
    response = requests.post(url, json=payload.dict())
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )


def test_add_duplicate_work(up_test_dbase, clear_deposits_table):
    up_test_dbase.add_deposit_info(area_name='test-area')

    table = Table('deposits')
    query = str(
        Query.from_(table).select('id').where(
            table.area_name == 'test-area'
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    area_id = cursor.fetchone()[0]

    url = f'{URL}/add-work-info'
    payload = WorkInfo(
        well_name='test-name',
        datetime_start_str='2022-11-15 12:12:12',
        work_type='test-work',
        deposit_id=area_id
    )
    requests.post(url, json=payload.dict())

    expected_value = {
        'status': False,
        'message': (f'Cant add work info: {payload.well_name}, '
                    f'{payload.datetime_start_str}, {payload.work_type}, '
                    f'{payload.deposit_id}'),
        'data': {}
    }
    response = requests.post(url, json=payload.dict())
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )


def test_update_work_info(up_test_dbase, clear_deposits_table):
    up_test_dbase.add_deposit_info(area_name='test-area')
    table = Table('deposits')
    query = str(
        Query.from_(table).select('id').where(
            table.area_name == 'test-area'
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    area_id = cursor.fetchone()[0]

    old_work_info = WorkInfo(
        well_name='test-name',
        datetime_start_str='2022-11-15 12:12:12',
        work_type='test-work',
        deposit_id=area_id
    )
    up_test_dbase.add_work_info(work_info=old_work_info)

    new_work_info = WorkInfo(
        well_name='test-name2',
        datetime_start_str='2022-11-20 10:10:10',
        work_type='test-work2',
        deposit_id=area_id
    )
    payload = {
        'old_work_info': old_work_info.dict(),
        'new_work_info': new_work_info.dict()
    }
    excepted_value = {
        'status': True,
        'message': (
            f'Work info "{old_work_info.well_name}", '
            f'"{old_work_info.datetime_start_str}", '
            f'"{old_work_info.work_type}","{old_work_info.deposit_id}" '
            f'successfully changed to "{new_work_info.well_name}", '
            f'"{new_work_info.datetime_start_str}", '
            f'"{new_work_info.work_type}", "{new_work_info.deposit_id}".'
        ),
        'data': {}
    }
    url = f'{URL}/update-work-info'
    response = requests.post(url, json=payload)
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(excepted_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )


def test_update_duplicate_work_info(up_test_dbase,
                                    clear_deposits_table):
    up_test_dbase.add_deposit_info(area_name='test-area')
    table = Table('deposits')
    query = str(
        Query.from_(table).select('id').where(
            table.area_name == 'test-area'
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    area_id = cursor.fetchone()[0]

    work_info = WorkInfo(
        well_name='test-name',
        datetime_start_str='2022-11-15 12:12:12',
        work_type='test-work',
        deposit_id=area_id
    )
    up_test_dbase.add_work_info(work_info=work_info)

    old_work_info = WorkInfo(
        well_name='test-name1',
        datetime_start_str='2022-11-21 12:12:12',
        work_type='test-work1',
        deposit_id=area_id
    )
    up_test_dbase.add_work_info(work_info=old_work_info)

    new_work_info = WorkInfo(
        well_name='test-name',
        datetime_start_str='2022-11-15 12:12:12',
        work_type='test-work',
        deposit_id=area_id
    )
    payload = {
        'old_work_info': old_work_info.dict(),
        'new_work_info': new_work_info.dict()
    }
    excepted_value = {
        'status': False,
        'message': (
            f'Cant change "{old_work_info.well_name}", '
            f'"{old_work_info.datetime_start_str}", '
            f'"{old_work_info.work_type}","{old_work_info.deposit_id}" '
            f'to "{new_work_info.well_name}", '
            f'"{new_work_info.datetime_start_str}", '
            f'"{new_work_info.work_type}", "{new_work_info.deposit_id}".'
        ),
        'data': {}
    }
    url = f'{URL}/update-work-info'
    response = requests.post(url, json=payload)
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(excepted_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )


def test_get_works_info(up_test_dbase, clear_deposits_table):
    up_test_dbase.add_deposit_info(area_name='test-area')

    table = Table('deposits')
    query = str(
        Query.from_(table).select('id').where(
            table.area_name == 'test-area'
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    area_id = cursor.fetchone()[0]

    first_work_info = WorkInfo(
        well_name='test-name',
        datetime_start_str='2022-11-15 12:12:12',
        work_type='test-work',
        deposit_id=area_id
    )
    up_test_dbase.add_work_info(work_info=first_work_info)

    second_work_info = WorkInfo(
        well_name='test-name2',
        datetime_start_str='2000-01-24 11:12:13',
        work_type='test-work2',
        deposit_id=area_id
    )
    up_test_dbase.add_work_info(work_info=second_work_info)

    url = f'{URL}/get-works-info/{area_id}'
    response = requests.get(url)

    expected_value = {
        'status': True,
        'message': (
            f'All works related to deposit with id:'
            f'{area_id} returend successfully'
        ),
        'data': {
            'works_info': [
                first_work_info, second_work_info
            ]

        }
    }
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )

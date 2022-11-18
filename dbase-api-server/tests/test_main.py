import os

import requests
from dotenv import load_dotenv
from hamcrest import assert_that, equal_to
from pypika import Query, Table

from dbase_api_server.models import Deposit, WorkInfo

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
    up_test_dbase.add_deposit_info('test-area')

    table = Table('deposits')
    query = str(
        Query.from_(table).select('id').where(
            table.area_name == 'test-area'
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    area_id = cursor.fetchone()[0]

    well_name = 'test-name'
    datetime_start_str = '2022-11-15 12:12:12'
    work_type = 'test-work'
    deposit_id = area_id

    url = f'{URL}/add-work-info'
    payload = WorkInfo(
        well_name=well_name,
        datetime_start_str=datetime_start_str,
        work_type=work_type,
        deposit_id=deposit_id
    )
    expected_value = {
        'status': True,
        'message': (f'Successfully added work info: {well_name}, '
                    f'{datetime_start_str}, {work_type}, {deposit_id}'),
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
    up_test_dbase.add_deposit_info('test-area')

    table = Table('deposits')
    query = str(
        Query.from_(table).select('id').where(
            table.area_name == 'test-area'
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    area_id = cursor.fetchone()[0]

    well_name = 'test-name'
    datetime_start_str = '2022-11-15 12:12:12'
    work_type = 'test-work'
    deposit_id = area_id

    url = f'{URL}/add-work-info'
    payload = WorkInfo(
        well_name=well_name,
        datetime_start_str=datetime_start_str,
        work_type=work_type,
        deposit_id=deposit_id
    )
    requests.post(url, json=payload.dict())

    expected_value = {
        'status': False,
        'message': (f'Cant add work info: {well_name}, '
                    f'{datetime_start_str}, {work_type}, {deposit_id}'),
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

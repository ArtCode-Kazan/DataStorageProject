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

    old_well_name = 'test-name'
    old_datetime_start_str = '2022-11-15 12:12:12'
    old_work_type = 'test-work'
    old_deposit_id = area_id

    old_work_info = WorkInfo(
        well_name=old_well_name,
        datetime_start_str=old_datetime_start_str,
        work_type=old_work_type,
        deposit_id=old_deposit_id
    )
    up_test_dbase.add_work_info(old_work_info)

    new_well_name = 'test-name2'
    new_datetime_start_str = '2022-11-20 10:10:10'
    new_work_type = 'test-work2'
    new_deposit_id = area_id

    new_work_info = WorkInfo(
        well_name=new_well_name,
        datetime_start_str=new_datetime_start_str,
        work_type=new_work_type,
        deposit_id=new_deposit_id
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

    well_name = 'test-name'
    datetime_start_str = '2022-11-15 12:12:12'
    work_type = 'test-work'
    deposit_id = area_id

    work_info = WorkInfo(
        well_name=well_name,
        datetime_start_str=datetime_start_str,
        work_type=work_type,
        deposit_id=deposit_id
    )
    up_test_dbase.add_work_info(work_info)

    old_well_name = 'test-name1'
    old_datetime_start_str = '2022-11-21 12:12:12'
    old_work_type = 'test-work1'
    old_deposit_id = area_id

    old_work_info = WorkInfo(
        well_name=old_well_name,
        datetime_start_str=old_datetime_start_str,
        work_type=old_work_type,
        deposit_id=old_deposit_id
    )
    up_test_dbase.add_work_info(old_work_info)

    new_well_name = 'test-name'
    new_datetime_start_str = '2022-11-15 12:12:12'
    new_work_type = 'test-work'
    new_deposit_id = area_id

    new_work_info = WorkInfo(
        well_name=new_well_name,
        datetime_start_str=new_datetime_start_str,
        work_type=new_work_type,
        deposit_id=new_deposit_id
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
    area_name = 'test-area'
    up_test_dbase.add_deposit_info(area_name)

    table = Table('deposits')
    query = str(
        Query.from_(table).select('id').where(
            table.area_name == 'test-area'
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    area_id = cursor.fetchone()[0]

    first_well_name = 'test-name'
    first_datetime_start_str = '2022-11-15 12:12:12'
    first_work_type = 'test-work'
    first_deposit_id = area_id

    first_work_info = WorkInfo(
        well_name=first_well_name,
        datetime_start_str=first_datetime_start_str,
        work_type=first_work_type,
        deposit_id=first_deposit_id
    )
    up_test_dbase.add_work_info(first_work_info)

    second_well_name = 'test-name2'
    second_datetime_start_str = '2000-01-24 11:12:13'
    second_work_type = 'test-work2'
    second_deposit_id = area_id

    second_work_info = WorkInfo(
        well_name=second_well_name,
        datetime_start_str=second_datetime_start_str,
        work_type=second_work_type,
        deposit_id=second_deposit_id
    )
    up_test_dbase.add_work_info(second_work_info)

    url = f'{URL}/get-works-info/{area_id}'
    response = requests.get(url)

    expected_value = {
        'status': True,
        'message': (
            f'All works related to deposit with id:'
            f'{area_id} returend successfully'
        ),
        'data': {
            'work_info': [
                first_work_info.dict(), second_work_info.dict()
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


def test_add_station_info(up_test_dbase, clear_deposits_table):
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

    table = Table('works')
    query = str(
        Query.from_(table).select('id').where(
            table.well_name == work_info.well_name).where(
            table.start_time == work_info.datetime_start_str).where(
            table.work_type == work_info.work_type).where(
            table.deposit_id == work_info.deposit_id
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    work_id_value = cursor.fetchone()[0]

    payload = StationInfo(
        station_number=666,
        x_wgs84=11.11111111,
        y_wgs84=22.22222222,
        altitude=33.333333,
        work_id=work_id_value
    )
    url = f'{URL}/add-station-info'
    expected_value = {
        'status': True,
        'message': (
            f'Successfully added station info: {payload.station_number}, '
            f'{payload.x_wgs84}, {payload.y_wgs84}, '
            f'{payload.altitude}, {payload.work_id}'
        ),
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


def test_add_duplicate_station_info(up_test_dbase, clear_deposits_table):
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

    table = Table('works')
    query = str(
        Query.from_(table).select('id').where(
            table.well_name == work_info.well_name).where(
            table.start_time == work_info.datetime_start_str).where(
            table.work_type == work_info.work_type).where(
            table.deposit_id == work_info.deposit_id
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    work_id_value = cursor.fetchone()[0]

    payload = StationInfo(
        station_number=666,
        x_wgs84=11.11111111,
        y_wgs84=22.22222222,
        altitude=33.333333,
        work_id=work_id_value
    )
    url = f'{URL}/add-station-info'
    requests.post(url, json=payload.dict())

    expected_value = {
        'status': False,
        'message': (
            f'Cant add station info: {payload.station_number}, '
            f'{payload.x_wgs84}, {payload.y_wgs84}, {payload.altitude}, '
            f'{payload.work_id}'
        ),
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


def test_update_station_info(up_test_dbase, clear_deposits_table):
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

    table = Table('works')
    query = str(
        Query.from_(table).select('id').where(
            table.well_name == work_info.well_name).where(
            table.start_time == work_info.datetime_start_str).where(
            table.work_type == work_info.work_type).where(
            table.deposit_id == work_info.deposit_id
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    work_id_value = cursor.fetchone()[0]

    old_station_info = StationInfo(
        station_number=666,
        x_wgs84=11.11111111,
        y_wgs84=22.22222222,
        altitude=33.333333,
        work_id=work_id_value
    )
    url = f'{URL}/add-station-info'
    requests.post(url, json=old_station_info.dict())

    new_station_info = StationInfo(
        station_number=777,
        x_wgs84=55.11111111,
        y_wgs84=66.22222222,
        altitude=77.333333,
        work_id=work_id_value
    )
    expected_value = {
        'status': True,
        'message': (
            f'Successfully changed station info: '
            f'{old_station_info.station_number}, {old_station_info.x_wgs84}, '
            f'{old_station_info.y_wgs84}, {old_station_info.altitude}, '
            f'{old_station_info.work_id} '
            f'to {new_station_info.station_number}, '
            f'{new_station_info.x_wgs84}, {new_station_info.y_wgs84},'
            f' {new_station_info.altitude}, {new_station_info.work_id}.'
        ),
        'data': {}
    }
    payload = {
        'old_station_info': old_station_info.dict(),
        'new_station_info': new_station_info.dict()
    }
    url = f'{URL}/update-station-info'
    response = requests.post(url, json=payload)
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )


def test_update_duplicate_station_info(up_test_dbase, clear_deposits_table):
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

    table = Table('works')
    query = str(
        Query.from_(table).select('id').where(
            table.well_name == work_info.well_name).where(
            table.start_time == work_info.datetime_start_str).where(
            table.work_type == work_info.work_type).where(
            table.deposit_id == work_info.deposit_id
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    work_id_value = cursor.fetchone()[0]

    payload = StationInfo(
        station_number=666,
        x_wgs84=11.111111,
        y_wgs84=22.222222,
        altitude=33.3,
        work_id=work_id_value
    )
    url = f'{URL}/add-station-info'
    requests.post(url, json=payload.dict())

    old_station_info = StationInfo(
        station_number=777,
        x_wgs84=55.111111,
        y_wgs84=99.222222,
        altitude=66.3,
        work_id=work_id_value
    )
    url = f'{URL}/add-station-info'
    requests.post(url, json=payload.dict())

    new_station_info = StationInfo(
        station_number=666,
        x_wgs84=11.111111,
        y_wgs84=22.222222,
        altitude=33.3,
        work_id=work_id_value
    )
    expected_value = {
        'status': True,
        'message': (
            f'Successfully changed station info: '
            f'{old_station_info.station_number}, {old_station_info.x_wgs84}, '
            f'{old_station_info.y_wgs84}, {old_station_info.altitude},'
            f' {old_station_info.work_id} '
            f'to {new_station_info.station_number}, '
            f'{new_station_info.x_wgs84}, {new_station_info.y_wgs84}, '
            f'{new_station_info.altitude}, {new_station_info.work_id}.'
        ),
        'data': {}
    }
    payload = {
        'old_station_info': old_station_info.dict(),
        'new_station_info': new_station_info.dict()
    }
    url = f'{URL}/update-station-info'
    response = requests.post(url, json=payload)
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )


def test_get_stations_info(up_test_dbase, clear_deposits_table):
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

    table = Table('works')
    query = str(
        Query.from_(table).select('id').where(
            table.well_name == work_info.well_name).where(
            table.start_time == work_info.datetime_start_str).where(
            table.work_type == work_info.work_type).where(
            table.deposit_id == work_info.deposit_id
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    work_id_value = cursor.fetchone()[0]

    first_station_info = StationInfo(
        station_number=666,
        x_wgs84=11.111111,
        y_wgs84=22.222222,
        altitude=33.3,
        work_id=work_id_value
    )
    up_test_dbase.add_station_info(station_info=first_station_info)

    second_station_info = StationInfo(
        station_number=777,
        x_wgs84=88.111111,
        y_wgs84=66.222222,
        altitude=44.3,
        work_id=work_id_value
    )
    up_test_dbase.add_station_info(station_info=second_station_info)

    url = f'{URL}/get-stations-info/{work_id_value}'
    response = requests.get(url)

    expected_value = {
        'status': True,
        'message': (
            f'All works related to work with id:"{work_id_value}" '
            f'returend successfully'
        ),
        'data': {
            'stations_info': [
                first_station_info.dict(),
                second_station_info.dict()
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

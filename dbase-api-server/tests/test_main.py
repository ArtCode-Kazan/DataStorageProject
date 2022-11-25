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


def test_add_station_info(up_test_dbase, clear_deposits_table):
    area_name = 'test-area'
    up_test_dbase.add_deposit_info(area_name=area_name)
    table = Table('deposits')
    query = str(
        Query.from_(table).select('id').where(
            table.area_name == area_name
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
    up_test_dbase.add_work_info(work_info=work_info)

    table = Table('works')
    query = str(
        Query.from_(table).select('id').where(
            table.well_name == well_name).where(
            table.start_time == datetime_start_str).where(
            table.work_type == work_type).where(
            table.deposit_id == deposit_id
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    work_id_value = cursor.fetchone()[0]

    station_number = 666
    x_wgs84 = 11.11111111
    y_wgs84 = 22.22222222
    altitude = 33.333333
    work_id = work_id_value

    payload = StationInfo(
        station_number=station_number,
        x_wgs84=x_wgs84,
        y_wgs84=y_wgs84,
        altitude=altitude,
        work_id=work_id
    )
    url = f'{URL}/add-station-info'
    expected_value = {
        'status': True,
        'message': (
            f'Successfully added station info: {station_number}, '
            f'{x_wgs84}, {y_wgs84}, {altitude}, {work_id}'
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
    area_name = 'test-area'
    up_test_dbase.add_deposit_info(area_name=area_name)
    table = Table('deposits')
    query = str(
        Query.from_(table).select('id').where(
            table.area_name == area_name
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
    up_test_dbase.add_work_info(work_info=work_info)

    table = Table('works')
    query = str(
        Query.from_(table).select('id').where(
            table.well_name == well_name).where(
            table.start_time == datetime_start_str).where(
            table.work_type == work_type).where(
            table.deposit_id == deposit_id
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    work_id_value = cursor.fetchone()[0]

    station_number = 666
    x_wgs84 = 11.11111111
    y_wgs84 = 22.22222222
    altitude = 33.333333
    work_id = work_id_value

    payload = StationInfo(
        station_number=station_number,
        x_wgs84=x_wgs84,
        y_wgs84=y_wgs84,
        altitude=altitude,
        work_id=work_id
    )
    url = f'{URL}/add-station-info'
    requests.post(url, json=payload.dict())

    expected_value = {
        'status': True,
        'message': (
            f'Cant add station info:  {station_number}, '
            f'{x_wgs84}, {y_wgs84}, {altitude}, {work_id}'
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
    area_name = 'test-area'
    up_test_dbase.add_deposit_info(area_name=area_name)
    table = Table('deposits')
    query = str(
        Query.from_(table).select('id').where(
            table.area_name == area_name
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
    up_test_dbase.add_work_info(work_info=work_info)

    table = Table('works')
    query = str(
        Query.from_(table).select('id').where(
            table.well_name == well_name).where(
            table.start_time == datetime_start_str).where(
            table.work_type == work_type).where(
            table.deposit_id == deposit_id
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    work_id_value = cursor.fetchone()[0]

    old_station_number = 666
    old_x_wgs84 = 11.11111111
    old_y_wgs84 = 22.22222222
    old_altitude = 33.333333
    old_work_id = work_id_value

    payload = StationInfo(
        station_number=old_station_number,
        x_wgs84=old_x_wgs84,
        y_wgs84=old_y_wgs84,
        altitude=old_altitude,
        work_id=old_work_id
    )
    url = f'{URL}/add-station-info'
    requests.post(url, json=payload.dict())

    new_station_number = 777
    new_x_wgs84 = 55.11111111
    new_y_wgs84 = 66.22222222
    new_altitude = 77.333333
    new_work_id = work_id_value

    payload = StationInfo(
        station_number=new_station_number,
        x_wgs84=new_x_wgs84,
        y_wgs84=new_y_wgs84,
        altitude=new_altitude,
        work_id=new_work_id
    )
    expected_value = {
        'status': True,
        'message': (
            f'Successfully changed station info: '
            f'{old_station_number}, {old_x_wgs84}, {old_y_wgs84}, '
            f'{old_altitude}, {old_work_id} '
            f'to {new_station_number}, {new_x_wgs84}, {new_y_wgs84}, '
            f'{new_altitude}, {new_work_id}.'
        ),
        'data': {}
    }
    url = f'{URL}/update-station-info'
    response = requests.post(url, json=payload.dict())
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )


def test_update_duplicate_station_info(up_test_dbase, clear_deposits_table):
    area_name = 'test-area'
    up_test_dbase.add_deposit_info(area_name=area_name)
    table = Table('deposits')
    query = str(
        Query.from_(table).select('id').where(
            table.area_name == area_name
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
    up_test_dbase.add_work_info(work_info=work_info)

    table = Table('works')
    query = str(
        Query.from_(table).select('id').where(
            table.well_name == well_name).where(
            table.start_time == datetime_start_str).where(
            table.work_type == work_type).where(
            table.deposit_id == deposit_id
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    work_id_value = cursor.fetchone()[0]

    station_number = 666
    x_wgs84 = 11.11111111
    y_wgs84 = 22.22222222
    altitude = 33.333333
    work_id = work_id_value

    payload = StationInfo(
        station_number=station_number,
        x_wgs84=x_wgs84,
        y_wgs84=y_wgs84,
        altitude=altitude,
        work_id=work_id
    )
    url = f'{URL}/add-station-info'
    requests.post(url, json=payload.dict())

    old_station_number = 777
    old_x_wgs84 = 55.11111111
    old_y_wgs84 = 99.22222222
    old_altitude = 66.333333
    old_work_id = work_id_value

    payload = StationInfo(
        station_number=old_station_number,
        x_wgs84=old_x_wgs84,
        y_wgs84=old_y_wgs84,
        altitude=old_altitude,
        work_id=old_work_id
    )
    url = f'{URL}/add-station-info'
    requests.post(url, json=payload.dict())

    new_station_number = 666
    new_x_wgs84 = 11.11111111
    new_y_wgs84 = 22.22222222
    new_altitude = 33.333333
    new_work_id = work_id_value

    payload = StationInfo(
        station_number=new_station_number,
        x_wgs84=new_x_wgs84,
        y_wgs84=new_y_wgs84,
        altitude=new_altitude,
        work_id=new_work_id
    )
    expected_value = {
        'status': True,
        'message': (
            f'Cant change station info: {old_station_number}, '
            f'{old_x_wgs84}, {old_y_wgs84}, '
            f'{old_altitude}, {old_work_id} '
            f'to {new_station_number}, {new_x_wgs84}, {new_y_wgs84}, '
            f'{new_altitude}, {new_work_id}.'
        ),
        'data': {}
    }
    url = f'{URL}/update-station-info'
    response = requests.post(url, json=payload.dict())
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )


def test_get_stations_info(self, up_test_dbase, clear_deposits_table):
    area_name = 'test-area'
    up_test_dbase.add_deposit_info(area_name=area_name)
    table = Table('deposits')
    query = str(
        Query.from_(table).select('id').where(
            table.area_name == area_name
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
    up_test_dbase.add_work_info(work_info=work_info)

    table = Table('works')
    query = str(
        Query.from_(table).select('id').where(
            table.well_name == well_name).where(
            table.start_time == datetime_start_str).where(
            table.work_type == work_type).where(
            table.deposit_id == deposit_id
        )
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query)
    work_id_value = cursor.fetchone()[0]

    first_station_number = 666
    first_x_wgs84 = 11.111111
    first_y_wgs84 = 22.222222
    first_altitude = 33.3
    first_work_id = work_id_value

    first_station_info = StationInfo(
        station_number=first_station_number,
        x_wgs84=first_x_wgs84,
        y_wgs84=first_y_wgs84,
        altitude=first_altitude,
        work_id=first_work_id
    )
    up_test_dbase.add_station_info(station_info=first_station_info)

    second_station_number = 777
    second_x_wgs84 = 88.111111
    second_y_wgs84 = 66.222222
    second_altitude = 44.3
    second_work_id = work_id_value

    second_station_info = StationInfo(
        station_number=second_station_number,
        x_wgs84=second_x_wgs84,
        y_wgs84=second_y_wgs84,
        altitude=second_altitude,
        work_id=second_work_id
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
        'data': [
            ['station_number', first_station_number],
            ['x_wgs84', first_x_wgs84],
            ['y_wgs84', first_y_wgs84],
            ['altitude', first_altitude],
            ['work_id', first_work_id],
            ['station_number', second_station_number],
            ['x_wgs84', second_x_wgs84],
            ['y_wgs84', second_y_wgs84],
            ['altitude', second_altitude],
            ['work_id', second_work_id]
        ]
    }
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )

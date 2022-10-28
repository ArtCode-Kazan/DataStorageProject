import os

import requests
from dotenv import load_dotenv
from hamcrest import assert_that, equal_to

load_dotenv()

APP_HOST = os.getenv('APP_HOST')
APP_PORT = os.getenv('APP_PORT')


def test_get_all_deposits(up_test_dbase, clear_deposits_table):
    url = f'http://{APP_HOST}:{APP_PORT}/get-all-deposits'
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


def test_add_new_deposit_name(clear_deposits_table):
    payload = {'area_name': 'test-name'}
    url = f'http://{APP_HOST}:{APP_PORT}/add-deposit'
    response = requests.post(url, params=payload)
    expected_value = {
        'status': True,
        'message': f'Deposit name "{payload["area_name"]}" added successfully',
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

    payload = {'area_name': ''}
    expected_value = {
        'status': False,
        'message': f'Cant add deposit name "{payload["area_name"]}"',
        'data': {}
    }
    url = f'http://{APP_HOST}:{APP_PORT}/add-deposit'
    response = requests.post(url, params=payload)
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )


def test_update_deposit_name(up_test_dbase, clear_deposits_table):
    old_area_name = 'test-name'
    up_test_dbase.add_deposit_info(area_name=old_area_name)

    payload = {
        'old_area_name': 'test-name',
        'new_area_name': 'test-name-2'
    }
    expected_value = {
        'status': True,
        'message': (f'Deposit "{payload["old_area_name"]}" successfully '
                    f'renamed to "{payload["new_area_name"]}"'),
        'data': {}
    }
    url = (f'http://{APP_HOST}:{APP_PORT}/update-deposit')
    response = requests.post(url, params=payload)
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )

    payload = {
        'old_area_name': 'test-name-2',
        'new_area_name': ''
    }
    expected_value = {
        'status': False,
        'message': (f'Cant rename "{payload["old_area_name"]} '
                    f'to "{payload["new_area_name"]}"'),
        'data': {}
    }
    url = (f'http://{APP_HOST}:{APP_PORT}/update-deposit')
    response = requests.post(url, params=payload)
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(requests.codes.ok)
    )

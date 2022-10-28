import os

import requests
from dotenv import load_dotenv
from hamcrest import assert_that, equal_to

load_dotenv()

app_host = os.getenv('APP_HOST')
app_port = os.getenv('APP_PORT')


def test_get_all_deposists(up_test_dbase, clear_deposits_table):
    url = f'http://{app_host}:{app_port}/get-all-deposits'
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
        matcher=equal_to(200)
    )


def test_add_new_deposit_name(clear_deposits_table):
    area_name = 'test-name'
    expected_value = {
        'status': True,
        'message': f'Deposit name "{area_name}" added successfully',
        'data': {}
    }
    url = f'http://{app_host}:{app_port}/add-deposit?area_name={area_name}'
    response = requests.post(url)
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )

    area_name = ''
    expected_value = {
        'status': False,
        'message': f'Cant add deposit name "{area_name}"',
        'data': {}
    }
    url = f'http://{app_host}:{app_port}/add-deposit?area_name={area_name}'
    response = requests.post(url)
    assert_that(
        actual_or_assertion=response.json(),
        matcher=equal_to(expected_value)
    )
    assert_that(
        actual_or_assertion=response.status_code,
        matcher=equal_to(200)
    )

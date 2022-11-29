import pytest
from pypika import Query, Table
from testing_environment import TestEnvironment

from dbase_api_server.dbase import StorageDBase


@pytest.fixture(scope='session')
def up_test_dbase():
    environment = TestEnvironment(is_update_images=True)
    environment.initialize()
    test_dbase = StorageDBase(params=environment.dbase_connection_params)
    yield test_dbase
    environment.finalize()


@pytest.fixture
def clear_deposits_table(up_test_dbase):
    yield
    table = Table('deposits')
    query = str(
        Query.from_(table).delete()
    )
    cursor = up_test_dbase.connection.cursor()
    cursor.execute(query=query)
    up_test_dbase.connection.commit()


@pytest.fixture
def fill_deposit_names(up_test_dbase, clear_deposits_table):
    area_names = [f'test-area-{x}' for x in range(20)]
    table = Table('deposits')
    for area_name in area_names:
        query = str(
            Query.into(table).columns(table.area_name).insert(area_name)
        )
        cursor = up_test_dbase.connection.cursor()
        cursor.execute(query=query)
    up_test_dbase.connection.commit()
    yield len(area_names)

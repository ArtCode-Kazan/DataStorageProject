import pytest
from testing_environment import TestEnvironment

from dbase_api_server.dbase import StorageDBase


@pytest.fixture(scope='session')
def up_test_dbase():
    environment = TestEnvironment()
    environment.initialize()
    test_dbase = StorageDBase(params=environment.connection_params)
    yield test_dbase
    environment.finalize()

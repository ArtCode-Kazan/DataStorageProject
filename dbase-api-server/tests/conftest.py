import pytest

from testing_environment import TestEnvironment


@pytest.fixture(scope='session')
def up_environment():
    environment = TestEnvironment()
    environment.initialize()
    yield environment
    environment.finalize()

from hamcrest import assert_that, equal_to, is_

from dbase_api_server.containers import (PostgresConnectionParams,
                                         UvicornConnectionParams)


class TestPostgresConnectionParams:
    host = 'some-host'
    port = 7777
    user = 'some-user'
    password = 'some-password'
    dbname = 'some-dbase'

    obj = PostgresConnectionParams(
        host=host, port=port, user=user, password=password, dbname=dbname
    )

    def test_docker_env(self):
        expected_value = [
            f'POSTGRES_USER={self.user}',
            f'POSTGRES_PASSWORD={self.password}',
            f'POSTGRES_DB={self.dbname}'
        ]

        assert_that(
            actual_or_assertion=self.obj.docker_env,
            matcher=equal_to(expected_value)
        )

    def test_connection_string(self):
        assert_that(
            actual_or_assertion=isinstance(self.obj.connection_string, str),
            matcher=is_(True)
        )

        expected_value = (
            f'host={self.host} port={self.port} '
            f'user={self.user} password={self.password} '
            f'dbname={self.dbname}'
        )
        assert_that(
            actual_or_assertion=self.obj.connection_string,
            matcher=equal_to(expected_value)
        )


class TestUvicornConnectionParams:
    host = 'some-host'
    port = 1234
    url_address = 'http://some-host:1234'

    obj = UvicornConnectionParams(host=host, port=port)

    def test_url_address(self):
        assert_that(
            actual_or_assertion=self.obj.url_address,
            matcher=equal_to(self.url_address)
        )

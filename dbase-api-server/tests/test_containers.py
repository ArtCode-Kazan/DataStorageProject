from hamcrest import assert_that, equal_to, is_

from dbase_api_server.containers import PostgresConnectionParams


class TestPostgresConnectionParams:
    host = 'some-host'
    port = 7777
    user = 'some-user'
    password = 'some-password'
    dbname = 'some-dbase'

    def create_object(self):
        return PostgresConnectionParams(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.dbname
        )

    def test_docker_env(self):
        params = self.create_object()

        expected_value = [
            f'POSTGRES_USER={self.user}',
            f'POSTGRES_PASSWORD={self.password}',
            f'POSTGRES_DB={self.dbname}'
        ]

        assert_that(
            actual_or_assertion=params.docker_env,
            matcher=equal_to(expected_value)
        )

    def test_connection_string(self):
        params = self.create_object()
        assert_that(
            actual_or_assertion=isinstance(params.connection_string, str),
            matcher=is_(True)
        )

        expected_value = (
            f'host={self.host} port={self.port} '
            f'user={self.user} password={self.password} '
            f'dbname={self.dbname}'
        )
        assert_that(
            actual_or_assertion=params.connection_string,
            matcher=equal_to(expected_value)
        )

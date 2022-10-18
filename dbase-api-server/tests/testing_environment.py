import os
import platform
import getpass

import dotenv

from dbase_api_server.containers import PostgresConnectionParams
from dbase_api_server.dbase import DEFAULT_PORT, DEFAULT_PATH

from environment import CustomDockerClient, Storage


LINUX_PLATFORM, WINDOWS_PLATFORM = 'linux', 'windows'
TEMP_FOLDERS = {
    LINUX_PLATFORM: '/tmp',
    WINDOWS_PLATFORM: os.path.join('C:/', 'Users', getpass.getuser(),
                                   'Appdata', 'Local', 'Temp')
}


DOCKER_FOLDER = 'postgres-server'
TMP_FOLDER = 'test-postgres'
IMAGE_NAME = 'test-postgres'
CONTAINER_NAME = 'test-postgres-container'


dotenv.load_dotenv()


class TestEnvironment:
    def __init__(self):
        self.__connection_params = PostgresConnectionParams(
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=int(os.getenv('POSTGRES_PORT')),
            database=os.getenv('POSTGRES_DBASE')
        )

        platform_name = platform.system().lower()
        try:
            temp_root = TEMP_FOLDERS[platform_name]
        except KeyError:
            raise KeyError('Unknown OS platform')

        self.__storage = Storage(root=temp_root, folder_name=TMP_FOLDER)
        self.__docker_client = CustomDockerClient()

    @property
    def connection_params(self) -> PostgresConnectionParams:
        return self.__connection_params

    @property
    def docker_client(self) -> CustomDockerClient:
        return self.__docker_client

    @property
    def storage(self) -> Storage:
        return self.__storage

    @property
    def root_folder(self) -> str:
        import dbase_api_server
        path = os.path.dirname(dbase_api_server.__file__)
        return os.path.split(os.path.split(path)[0])[0]

    @property
    def dockerfile_root(self) -> str:
        path = os.path.join(self.root_folder, DOCKER_FOLDER)
        if not os.path.exists(path):
            raise OSError('Folder with dockerfile not found')
        return path

    def start_docker_container(self):
        self.docker_client.create_image(
            docker_root=self.dockerfile_root,
            image_name=IMAGE_NAME
        )

        self.docker_client.run_container(
            image_name=IMAGE_NAME,
            environment_vars=self.connection_params.docker_env,
            ports={f'{DEFAULT_PORT}/tcp': self.connection_params.port},
            volumes=[f'{self.storage.path}:{DEFAULT_PATH}'],
            container_name=CONTAINER_NAME
        )

    def initialize(self):
        self.storage.create()
        self.start_docker_container()

    def finalize(self):
        self.docker_client.remove_container(container_name=CONTAINER_NAME)
        self.storage.clear()
        self.docker_client.remove_image(image_name=IMAGE_NAME)

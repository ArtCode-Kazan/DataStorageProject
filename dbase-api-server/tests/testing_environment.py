import os

import dotenv

from dbase_api_server.containers import ConnectionParams

from dbase_api_server.dbase import DEFAULT_PORT, DEFAULT_PATH

from environment.docker_client import CustomDockerClient
from environment.storage import Storage


import platform
import getpass


TEMP_FOLDERS = {
    'linux': '/tmp',
    'windows': os.path.join('C:/', 'Users', getpass.getuser(),
                            'Appdata', 'Local', 'Temp')
}


DOCKER_FOLDER = 'postgres-server'
TMP_FOLDER = 'test-postgres'
IMAGE_NAME = 'test-postgres'
CONTAINER_NAME = 'test-postgres-container'


dotenv.load_dotenv()


class TestEnvironment:
    def __init__(self):
        self.__connection_params = ConnectionParams(
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
    def connection_params(self) -> ConnectionParams:
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

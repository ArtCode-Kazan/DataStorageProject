import getpass
import os
import platform
import subprocess
from time import sleep
from typing import List, Tuple

import dotenv
import requests
from requests.exceptions import ConnectionError

from dbase_api_server.containers import (PostgresConnectionParams,
                                         UvicornConnectionParams)
from environment import CustomDockerClient, Storage

LINUX_PLATFORM, WINDOWS_PLATFORM = 'linux', 'windows'

TEMP_FOLDERS = {
    LINUX_PLATFORM: '/tmp',
    WINDOWS_PLATFORM: os.path.join('C:/', 'Users', getpass.getuser(),
                                   'Appdata', 'Local', 'Temp')
}

DOCKER_COMPOSE_FILE_TEMPLATE_NAME = 'docker_compose.yaml.template'
DOCKER_COMPOSE_FILENAME = 'docker-compose.yaml'

TMP_FOLDER_NAME = 'test-postgres'

POSTGRES_SERVER_FOLDER_NAME = 'postgres-server'
DBASE_API_SERVER_FOLDER_NAME = 'dbase-api-server'

CONTAINER_PREFIX = 'compose-container'
IMAGE_PREFIX = 'compose-image'


dotenv.load_dotenv()


def get_cmd_output(root: str, command: List[str]) -> Tuple[bool, List[str]]:
    os.chdir(root)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    output_text = proc.communicate()

    is_success = True if proc.wait() == 0 else False
    if is_success:
        return is_success, output_text[0].decode().split('\n')
    return is_success, []


class DockerComposeFileTemplate:
    def __init__(self, path: str):
        if not os.path.join(path):
            raise OSError('Docker compose file template not found')

        self.__origin_content = self.load(path)
        self.__changed_content = self.__origin_content

    @staticmethod
    def load(path: str) -> str:
        with open(path, 'r') as file_ctx:
            return file_ctx.read()

    @property
    def origin_content(self) -> str:
        return self.__origin_content

    @property
    def changed_content(self) -> str:
        return self.__changed_content

    @changed_content.setter
    def changed_content(self, value: str):
        self.__changed_content = value

    def replace(self, old_substring: str, new_substring: str):
        self.changed_content = self.changed_content.replace(
            old_substring, new_substring
        )

    def add_image_prefix(self, prefix_value: str):
        self.replace(
            old_substring='{image-prefix}',
            new_substring=prefix_value
        )

    def add_container_prefix(self, prefix_value: str):
        self.replace(
            old_substring='{container-prefix}',
            new_substring=prefix_value
        )

    def add_postgres_server_folder_path(self, path: str):
        self.replace(
            old_substring='{postgres-server-folder}',
            new_substring=path
        )

    def add_postgres_connection_params(self, params: PostgresConnectionParams):
        self.replace(
            old_substring='{POSTGRES_PORT}',
            new_substring=str(params.port)
        )

        self.replace(
            old_substring='{POSTGRES_USER}',
            new_substring=params.user
        )

        self.replace(
            old_substring='{POSTGRES_PASSWORD}',
            new_substring=params.password
        )

        self.replace(
            old_substring='{POSTGRES_DB}',
            new_substring=params.dbname
        )

    def add_inner_volume_path(self, path: str):
        self.replace(
            old_substring='{temp-storage-folder}',
            new_substring=path
        )

    def add_uvicorn_app_folder_path(self, path: str):
        self.replace(
            old_substring='{dbase-api-server-folder}',
            new_substring=path
        )

    def add_uvicorn_connection_params(self, params: UvicornConnectionParams):
        self.replace(
            old_substring='{APP_PORT}',
            new_substring=str(params.port)
        )

    def save(self, export_root: str):
        if not os.path.exists(export_root):
            raise OSError('Export root not found')
        export_path = os.path.join(export_root, DOCKER_COMPOSE_FILENAME)
        with open(export_path, 'w') as file_ctx:
            file_ctx.write(self.changed_content)


class TestEnvironment:
    def __init__(self, is_update_images: bool = True):
        self.__dbase_connection_params = PostgresConnectionParams(
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=int(os.getenv('POSTGRES_PORT')),
            dbname=os.getenv('POSTGRES_DB')
        )
        self.__uvicorn_dbase_params = UvicornConnectionParams(
            host=os.getenv('APP_HOST'),
            port=int(os.getenv('APP_PORT'))
        )

        self.__platform_name = platform.system().lower()
        try:
            self.__temp_root = TEMP_FOLDERS[self.__platform_name]
        except KeyError:
            raise KeyError('Unknown OS platform')

        self.__storage = Storage(
            root=self.__temp_root, folder_name=TMP_FOLDER_NAME
        )

        self.__docker_client = CustomDockerClient()
        if is_update_images:
            self.remove_images()

    @property
    def dbase_connection_params(self) -> PostgresConnectionParams:
        return self.__dbase_connection_params

    @property
    def uvicorn_connection_params(self) -> UvicornConnectionParams:
        return self.__uvicorn_dbase_params

    @property
    def platform_name(self) -> str:
        return self.__platform_name

    @property
    def tmp_root(self) -> str:
        return self.__temp_root

    @property
    def storage(self) -> Storage:
        return self.__storage

    @property
    def docker_client(self) -> CustomDockerClient:
        return self.__docker_client

    @property
    def root_folder(self) -> str:
        import dbase_api_server
        path = os.path.dirname(dbase_api_server.__file__)
        return os.path.split(os.path.split(path)[0])[0]

    @property
    def docker_compose_template_file_path(self) -> str:
        path = os.path.join(
            self.root_folder, DBASE_API_SERVER_FOLDER_NAME, 'tests',
            DOCKER_COMPOSE_FILE_TEMPLATE_NAME
        )
        return path

    @property
    def docker_compose_file_path(self) -> str:
        return os.path.join(self.tmp_root, DOCKER_COMPOSE_FILENAME)

    def create_docker_compose_file(self):
        file_template = DockerComposeFileTemplate(
            path=self.docker_compose_template_file_path
        )

        file_template.add_image_prefix(prefix_value=IMAGE_PREFIX)
        file_template.add_container_prefix(prefix_value=CONTAINER_PREFIX)

        file_template.add_postgres_server_folder_path(
            path=os.path.join(self.root_folder, POSTGRES_SERVER_FOLDER_NAME)
        )

        file_template.add_uvicorn_app_folder_path(
            path=os.path.join(self.root_folder, DBASE_API_SERVER_FOLDER_NAME)
        )

        file_template.add_inner_volume_path(path=self.storage.path)

        file_template.add_postgres_connection_params(
            params=self.dbase_connection_params
        )

        file_template.add_uvicorn_connection_params(
            params=self.uvicorn_connection_params
        )

        file_template.save(export_root=self.tmp_root)

    def start_docker_compose(self):
        if not os.path.exists(self.docker_compose_file_path):
            raise OSError('Docker compose file not found')
        command = ['docker-compose', 'up', '--detach']
        is_success, messages = get_cmd_output(
            root=self.tmp_root, command=command
        )
        if not is_success:
            raise RuntimeError('Docker compose starting is failed')

    def down_docker_compose(self):
        if not os.path.exists(self.docker_compose_file_path):
            raise OSError('Docker compose file not found')
        command = ['docker-compose', 'down']
        is_success, messages = get_cmd_output(
            root=self.tmp_root, command=command
        )
        if not is_success:
            raise RuntimeError('Docker compose off is failed')

    def is_dbase_api_server_exists(self, retrying=60, waiting=1) -> bool:
        ping_url = f'{self.uvicorn_connection_params.url_address}/ping'
        for _ in range(retrying):
            try:
                response = requests.get(url=ping_url)
                if response.status_code == requests.codes.ok:
                    return True
                sleep(waiting)
            except ConnectionError:
                sleep(waiting)
        return False

    def initialize(self):
        self.create_docker_compose_file()
        self.storage.create()

        self.start_docker_compose()
        if not self.is_dbase_api_server_exists():
            self.finalize()
            raise RuntimeError('Environment creation is failed')

    def remove_images(self):
        all_images = self.docker_client.images_tags
        for image_name in all_images:
            if IMAGE_PREFIX in image_name:
                self.docker_client.remove_image(image_name=image_name)
        self.docker_client.clear_system()

    def unblock_folder(self):
        if self.platform_name == LINUX_PLATFORM:
            login, password = os.getlogin(), os.getenv('SYSTEM_PASSWORD')
            path = self.storage.path
            command = f'echo {password} | sudo -S chown -R {login} {path}'
            subprocess.call(command, shell=True)

    def finalize(self):
        self.down_docker_compose()
        self.unblock_folder()
        self.storage.clear()
        os.remove(path=os.path.join(self.tmp_root, DOCKER_COMPOSE_FILENAME))

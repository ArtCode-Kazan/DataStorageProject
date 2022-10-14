"""
Модуль предназначен для работы с docker клиентом с помощью Docker SDK (Python).
"""

from typing import List, Dict, Set

import docker
from docker.client import DockerClient
from docker.models.containers import Container


class CustomDockerClient:
    """
    Класс-адаптер для удобной работы с docker-клиентом.
    """
    def __init__(self):
        """
        Конструктор класса. Здесь происходит сохранение docker-клиента.
        """
        self.__client = docker.from_env()

    @property
    def client(self) -> DockerClient:
        """
        Свойство возвращает адаптер подключения к docker.

        :return: docker-клиент
        """
        return self.__client

    @property
    def images_tags(self) -> Set[str]:
        """
        Свойство возвращает все имеющиеся уникальные названия образов.

        :return: коллекция образов
        """
        image_names = set()
        for image in self.client.images.list(all=True):
            image_names.add(image.tags[0].split(':')[0])
        return image_names

    def is_image_exist(self, image_name: str) -> bool:
        """
        Метод проверяет существование в системе образа с определенным именем.

        :param image_name: имя образа
        :return: True - если образ найден, False - если образ отсутствует
        """
        return image_name in self.images_tags

    def remove_image(self, image_name: str):
        """
        Метод удаляет образ из системы по его имени.

        :param image_name: имя образа
        :return: None
        """
        self.client.images.remove(image=image_name)

    def create_image(self, docker_root: str, image_name: str):
        """
        Метод создает образ в системе из Docker файла с указанным именем.

        :param docker_root: папка, где расположен Docker файл
        :param image_name: имя образа
        :return: None
        """
        self.client.images.build(path=docker_root, tag=image_name)

    def run_container(self, image_name: str, environment_vars: List[str],
                      ports: Dict[str, int], volumes: List[str],
                      container_name: str):
        """
        Метод запускает контейнер из образа, который уже есть в системе.

        Примеры записи входящих аргументов:
        environment_vars = ['POSTGRES_DBASE=my_dbase', 'POSTGRES_USER=mikko']

        ports = {'5432/tcp': 8133}.
        Здесь:
            - 5432 - порт внутри контейнера
            - tcp - тип соединения контейнера с хостом
            - 8133 - порт хоста

        volumes = ['my/folder/path:/var/lib/postgresql/data']

        :param image_name: имя образа
        :param environment_vars: список переменных окружения
        :param ports: словарь портов
        :param volumes: список точек монтирования файловых систем
        :param container_name: имя создаваемого контейнера
        :return: None
        """
        self.client.containers.run(
            image=image_name, environment=environment_vars, ports=ports,
            volumes=volumes, detach=True, name=container_name
        )

    def get_container_by_name(self, name: str) -> Container:
        """
        Метод возвращает объект контейнера по его имени.

        :param name: имя контейнера
        :return: Container
        """
        return self.client.containers.get(container_id=name)

    def clear_system(self):
        """
        Метод удаляет неиспользуемые контейнеры.

        :return: None
        """
        self.client.containers.prune()

    def remove_container(self, container_name: str):
        """
        Метод полностью удаляет контейнер из docker по его имени.
        :param container_name: имя контейнера
        :return: None
        """
        container = self.get_container_by_name(name=container_name)
        container.stop()
        self.clear_system()

"""
Модуль предназначен для работы с файловой системой компьютера
в случае создания окружения для каких-либо задач.
"""

import os
import shutil


class Storage:
    """
    Класс-обертка для управления доступом к хранилищу окружения
    """
    def __init__(self, root: str, folder_name: str):
        """
        Конструктор класса.

        :param root: корневой путь для создания папки хранилища окружения
        :param folder_name: имя папки хранилища окружения
        """
        if not os.path.exists(root):
            raise OSError('Invalid root path')

        self.__path = os.path.join(root, folder_name)

    @property
    def path(self) -> str:
        """
        Свойство возвращает полный путь к папке хранилища.

        :return: полный путь к папке хранилища
        """
        return self.__path

    def create(self):
        """
        Метод создает папку хранилища, если ее не существует.

        :return: None
        """
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def clear(self):
        """
        Метод удаляет папку хранилища, если папка существует.

        :return: None
        """
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

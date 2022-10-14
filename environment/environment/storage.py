import os
import shutil


class Storage:
    def __init__(self, root: str, folder_name: str):
        if not os.path.exists(root):
            raise OSError('Invalid root path')

        self.__path = os.path.join(root, folder_name)

    @property
    def path(self) -> str:
        return self.__path

    def create(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def clear(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

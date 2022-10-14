import os
import shutil
import platform
import getpass


TEMP_FOLDERS = {
    'linux': '/tmp',
    'windows': os.path.join('C:/', 'Users', getpass.getuser(),
                            'Appdata', 'Local', 'Temp')
}


class Storage:
    def __init__(self, folder_name: str):
        self.platform_name = platform.system().lower()
        try:
            self.temp_root = TEMP_FOLDERS[self.platform_name]
        except KeyError:
            raise KeyError('Unknown OS platform')

        self.__folder_name = folder_name

    @property
    def path(self) -> str:
        return os.path.join(self.temp_root, self.__folder_name)

    def create(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def clear(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

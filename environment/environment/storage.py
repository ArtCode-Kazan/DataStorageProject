"""Module for working with file system.

This module can help if you create temp folder for creation environment of
test session.

Examples:
    Storage initialization::

        from environment import Storage
        my_storage = Storage(root='/tmp', folder_name='my-tmp-folder')

    Storage creation::

        from environment import Storage

        my_storage = Storage(root='/tmp', folder_name='my-tmp-folder')
        my_storage.create()

    Storage deleting::

        from environment import Storage

        my_storage = Storage(root='/tmp', folder_name='my-tmp-folder')
        my_storage.clear()

"""

import os
import shutil


class Storage(object):
    """Class-adapter for access driving with environment storage."""
    def __init__(self, root: str, folder_name: str):
        """Initial class method.

        Args:
            root: root folder path for creating storage folder
            folder_name: storage folder name

        """
        if not os.path.exists(root):
            raise OSError('Invalid root path')

        self.__path = os.path.join(root, folder_name)

    @property
    def path(self) -> str:
        """Return full path to folder storage.

        Returns: full path

        """
        return self.__path

    def create(self):
        """Method creates storage folder if folder is exists.

        Returns: None

        """
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def clear(self):
        """Method remove storage folder if folder is exists.

        Returns: None

        """
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

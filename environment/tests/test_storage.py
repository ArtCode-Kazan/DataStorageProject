import os
from unittest.mock import Mock, PropertyMock, patch

import pytest
from hamcrest import assert_that, equal_to, is_

from environment.storage import Storage


class TestStorage:
    root = '/some/root'
    folder_name = 'abc'
    some_path = 'some-path'

    @patch('os.path.exists')
    def test_good_path(self, os_mock: Mock):
        os_mock.return_value = True

        storage_obj = Storage(root=self.root, folder_name=self.folder_name)

        os_mock.assert_called_once_with(self.root)
        full_path = os.path.join(self.root, self.folder_name)
        assert_that(
            actual_or_assertion=storage_obj.path,
            matcher=equal_to(full_path)
        )

    @patch('os.path.exists')
    def test_bad_path(self, os_mock: Mock):
        os_mock.return_value = False

        try:
            Storage(root=self.root, folder_name=self.folder_name)
            is_success = False
        except OSError:
            is_success = True

        os_mock.assert_called_once_with(self.root)
        assert_that(actual_or_assertion=is_success, matcher=is_(True))

    @pytest.mark.parametrize('is_path_exist', [True, False])
    @patch.object(Storage, 'path', new_callable=PropertyMock)
    @patch('os.mkdir')
    @patch('os.path.exists')
    def test_create(self, os_path_mock: Mock, os_mkdir_mock: Mock,
                    path_mock: Mock, is_path_exist: bool):
        os_path_mock.return_value = is_path_exist
        path_mock.return_value = self.some_path

        with patch('os.path.exists') as os_mock:
            os_mock.return_value = True
            storage = Storage(root=self.root, folder_name=self.folder_name)

        storage.create()

        os_path_mock.assert_called_once_with(self.some_path)
        if not is_path_exist:
            os_mkdir_mock.assert_called_once_with(self.some_path)
        else:
            os_mkdir_mock.assert_not_called()

    @pytest.mark.parametrize('is_path_exist', [True, False])
    @patch.object(Storage, 'path', new_callable=PropertyMock)
    @patch('shutil.rmtree')
    @patch('os.path.exists')
    def test_clear(self, os_path_mock: Mock, shutil_mock: Mock,
                   path_mock: Mock, is_path_exist: bool):
        os_path_mock.return_value = is_path_exist
        path_mock.return_value = self.some_path

        with patch('os.path.exists') as os_mock:
            os_mock.return_value = True
            storage = Storage(root=self.root, folder_name=self.folder_name)

        storage.clear()

        os_path_mock.assert_called_once_with(self.some_path)
        if is_path_exist:
            shutil_mock.assert_called_once_with(self.some_path)
        else:
            shutil_mock.assert_not_called()

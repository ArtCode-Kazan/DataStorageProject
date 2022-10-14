import os
from unittest.mock import Mock, PropertyMock, patch

import pytest
from hamcrest import assert_that, equal_to

from test_environment.storage import TEMP_FOLDERS
from test_environment.storage import Storage


class TestStorage:
    folder_name = 'abc'
    some_path = 'some-path'

    def create_object(self) -> Storage:
        return Storage(folder_name=self.folder_name)

    @pytest.mark.parametrize(
        'system_label, temp_folder_path', list(TEMP_FOLDERS.items()))
    @patch('platform.system')
    def test_good_platforms(self, platform_mock: Mock,
                            system_label: str, temp_folder_path: str):
        platform_mock.return_value = system_label.upper()

        storage = self.create_object()

        assert_that(
            actual_or_assertion=storage.temp_root,
            matcher=equal_to(temp_folder_path)
        )

        assert_that(
            actual_or_assertion=storage.path,
            matcher=equal_to(os.path.join(temp_folder_path, self.folder_name))
        )

    @patch('platform.system')
    def test_unknown_platform(self, platform_mock: Mock):
        platform_mock.return_value = 'unknown-platform'
        try:
            self.create_object()
            is_passed = False
        except KeyError:
            is_passed = True
        assert_that(actual_or_assertion=is_passed, matcher=equal_to(True))

    @pytest.mark.parametrize('is_path_exist', [True, False])
    @patch.object(Storage, 'path', new_callable=PropertyMock)
    @patch('os.mkdir')
    @patch('os.path.exists')
    def test_create(self, os_path_mock: Mock, os_mkdir_mock: Mock,
                    path_mock: Mock, is_path_exist: bool):
        os_path_mock.return_value = is_path_exist
        path_mock.return_value = self.some_path

        storage = self.create_object()
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

        storage = self.create_object()
        storage.clear()

        os_path_mock.assert_called_once_with(self.some_path)
        if is_path_exist:
            shutil_mock.assert_called_once_with(self.some_path)
        else:
            shutil_mock.assert_not_called()

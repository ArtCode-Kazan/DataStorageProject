from unittest.mock import Mock, PropertyMock, patch

from docker.models.containers import ContainerCollection
from docker.models.images import ImageCollection
from hamcrest import assert_that, equal_to, is_

from environment.docker_client import CustomDockerClient


class TestCustomDockerClient:
    some_value = 'some-value'
    some_folder = '/some/folder/path'

    @staticmethod
    def create_object() -> CustomDockerClient:
        return CustomDockerClient()

    @patch('docker.from_env')
    def test_init(self, docker_mock: Mock):
        docker_mock.return_value = self.some_value

        docker_obj = self.create_object()
        docker_mock.assert_called_once()

        assert_that(actual_or_assertion=docker_obj.client,
                    matcher=equal_to(self.some_value))

    @patch.object(ImageCollection, 'list')
    def test_images_tags(self, list_mock: Mock):
        test_tags = [
            ('a:v1', 'v1'),
            ('a:v2', 'v2'),
            ('b:v0', 'v0'),
            ('c:v0', 'v0'),
            ('d:v', 'v')
        ]

        test_images = []
        for tag in test_tags:
            image = Mock(tags=tag)
            test_images.append(image)

        list_mock.return_value = test_images
        tags = self.create_object().images_tags

        list_mock.assert_called_once_with(all=True)
        assert_that(actual_or_assertion=tags,
                    matcher=equal_to({'a', 'b', 'c', 'd'}))

    @patch.object(CustomDockerClient, 'images_tags', new_callable=PropertyMock)
    def test_is_image_exist(self, images_tags_mock: Mock):
        images_tags_mock.return_value = []

        docker_obj = self.create_object()
        assert_that(
            actual_or_assertion=docker_obj.is_image_exist(
                image_name=self.some_value
            ),
            matcher=is_(False)
        )

        images_tags_mock.return_value = [self.some_value]
        assert_that(
            actual_or_assertion=docker_obj.is_image_exist(
                image_name=self.some_value
            ),
            matcher=is_(True)
        )

    @patch.object(ImageCollection, 'remove')
    def test_remove_image(self, remove_mock: Mock):
        _ = self.create_object().remove_image(image_name=self.some_value)
        remove_mock.assert_called_once_with(image=self.some_value)

    @patch.object(ImageCollection, 'build')
    def test_build_image(self, build_mock: Mock):
        _ = self.create_object().create_image(
            docker_root=self.some_folder, image_name=self.some_value
        )
        build_mock.assert_called_once_with(
            path=self.some_folder, tag=self.some_value
        )

    @patch.object(ContainerCollection, 'run')
    def test_run_container(self, run_mock: Mock):
        image_name = 'image'
        envs = ['v', 'a', 'r', 's']
        ports = {'ports': 12345}
        volumes = ['volu:mes']
        container_name = 'container'
        _ = self.create_object().run_container(
            image_name=image_name, environment_vars=envs, ports=ports,
            volumes=volumes, container_name=container_name
        )

        run_mock.assert_called_once_with(
            image=image_name, environment=envs, ports=ports,
            volumes=volumes, name=container_name, detach=True
        )

    @patch.object(ContainerCollection, 'get')
    def test_get_container_by_name(self, get_mock: Mock):
        _ = self.create_object().get_container_by_name(name=self.some_value)
        get_mock.assert_called_once_with(container_id=self.some_value)

    @patch.object(ContainerCollection, 'prune')
    def test_get_clear_system(self, prune_mock: Mock):
        _ = self.create_object().clear_system()
        prune_mock.assert_called_once()

    @patch.object(CustomDockerClient, 'clear_system')
    @patch.object(CustomDockerClient, 'get_container_by_name')
    def test_remove_container(self, get_container_mock: Mock,
                              clear_system_mock: Mock):
        stop_mock = Mock(stop=Mock(return_value=True))
        get_container_mock.return_value = stop_mock
        obj = self.create_object()

        obj.remove_container(container_name=self.some_value)

        stop_mock.stop.assert_called_once()
        get_container_mock.assert_called_once_with(name=self.some_value)
        clear_system_mock.assert_called_once()

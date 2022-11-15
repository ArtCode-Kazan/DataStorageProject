"""Module for working with docker client using with Docker SDK (Python).

This module is useful working with docker client. You don't need use cmd line,
only simple Python class.

Examples:
    Initialization::

        from environment import CustomDockerClient
        docker_client = CustomDockerClient()

    Running container::

        docker_client.create_image(
            docker_root=dockerfile_root,
            image_name=image_name
        )

        docker_client.run_container(
            image_name=image_name,
            environment_vars=['param1:val1', 'param2:val2'],
            ports={'5432/tcp': 8133},
            volumes=['storage/path:my/path'],
            container_name=container_name
        )

"""

from typing import Dict, List, Set

import docker
from docker.client import DockerClient
from docker.models.containers import Container


class CustomDockerClient:
    """Class-adapter for simple working with docker client."""

    def __init__(self):
        """Initialize class method."""
        self.__client = docker.from_env()

    @property
    def client(self) -> DockerClient:
        """Return docker client object.

        Returns: DockerClient object

        """
        return self.__client

    @property
    def images_tags(self) -> Set[str]:
        """Return all (not none) unique image names in docker.

        Returns: collections of image names

        """
        image_names = set()
        for image in self.client.images.list(all=True):
            if not image.tags:
                continue
            image_names.add(image.tags[0].split(':')[0])
        return image_names

    @property
    def empty_image_ids(self) -> List[str]:
        """Return ids for all images with None name in docker system.

        Returns: list with short images ids

        """
        ids = []
        for image in self.client.images.list(all=True):
            if image.tags:
                continue
            ids.append(image.short_id.split(':')[1])
        return ids

    def is_image_exist(self, image_name: str) -> bool:
        """Return image existing by image name.

        Args:
            image_name: target image name

        Returns: True if image exists, False if image not found

        """
        return image_name in self.images_tags

    def remove_image(self, image_name_or_short_id: str):
        """Remove image by image name or short id.

        Args:
            image_name_or_short_id: target image name or short id

        Returns: None

        """
        self.client.images.remove(image=image_name_or_short_id)

    def create_image(self, docker_root: str, image_name: str):
        """Create image from dockerfile with target name.

        Args:
            docker_root: root path with dockerfile
            image_name: target image name

        Returns: None

        """
        self.client.images.build(path=docker_root, tag=image_name)

    def run_container(self, image_name: str, environment_vars: List[str],
                      ports: Dict[str, int], volumes: List[str],
                      container_name: str):
        """Run container from image. Image is exists in docker system.

        Notes:
            Examples of input arguments:
            ::

                environment_vars = [
                'POSTGRES_DBASE=my_dbase', 'POSTGRES_USER=mikko'
                ]
                ports = {'5432/tcp': 8133}

            Parameters for ports:
                - 5432 - port INSIDE container
                - tcp - connection type
                - 8133 - host port

        Args:
            image_name: target image name
            environment_vars: list of environment variables
            ports: dict of ports
            volumes: list of volumes
            container_name: target container name

        Returns: None

        """
        self.client.containers.run(
            image=image_name, environment=environment_vars, ports=ports,
            volumes=volumes, detach=True, name=container_name
        )

    def get_container_by_name(self, name: str) -> Container:
        """Return container object by container name.

        Args:
            name: target container name

        Returns: Container object

        """
        return self.client.containers.get(container_id=name)

    def remove_unused_containers(self):
        """Remove unused inactive containers from docker system.

        Returns: None

        """
        self.client.containers.prune()

    def remove_images_without_tag(self):
        """Remove images without tags.

        Returns: None

        """
        for short_id in self.empty_image_ids:
            self.remove_image(image_name_or_short_id=short_id)

    def clear_system(self):
        """Clear docker from unused inactive containers and none images.

        Returns: None

        """
        self.remove_unused_containers()
        self.remove_images_without_tag()

    def remove_container(self, container_name: str):
        """Remove container from docker with image by container name.

        Args:
            container_name: target container name

        Returns: None

        """
        container = self.get_container_by_name(name=container_name)
        container.stop()
        self.remove_unused_containers()

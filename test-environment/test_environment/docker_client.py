from typing import List, Dict, Set

import docker
from docker.client import DockerClient
from docker.models.containers import Container


class CustomDockerClient:
    def __init__(self):
        self.__client = docker.from_env()

    @property
    def client(self) -> DockerClient:
        return self.__client

    @property
    def images_tags(self) -> Set[str]:
        image_names = set()
        for image in self.client.images.list(all=True):
            image_names.add(image.tags[0].split(':')[0])
        return image_names

    def is_image_exist(self, image_name: str) -> bool:
        return image_name in self.images_tags

    def remove_image(self, image_name: str):
        self.client.images.remove(image=image_name)

    def create_image(self, docker_root: str, image_name: str):
        self.client.images.build(path=docker_root, tag=image_name)

    def run_container(self, image_name: str, environment_vars: List[str],
                      ports: Dict[str, int], volumes: List[str],
                      container_name: str):
        self.client.containers.run(
            image=image_name, environment=environment_vars, ports=ports,
            volumes=volumes, detach=True, name=container_name
        )

    def get_container_by_name(self, name: str) -> Container:
        return self.client.containers.get(container_id=name)

    def clear_system(self):
        self.client.containers.prune()

    def remove_container(self, container_name: str):
        container = self.get_container_by_name(name=container_name)
        container.stop()
        self.clear_system()

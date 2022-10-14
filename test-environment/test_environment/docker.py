from typing import List, Dict

import docker
from docker.client import DockerClient


class CustomDockerClient:
    def __init__(self):
        self.__client = docker.from_env()

    @property
    def client(self) -> DockerClient:
        return self.__client

    def is_image_exist(self, image_name: str) -> bool:
        images = self.client.images.list(name=image_name)
        return True if images else False

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

    def remove_container(self, container_name: str):
        container = self.client.containers.get(container_id=container_name)
        container.stop()
        self.client.containers.prune()

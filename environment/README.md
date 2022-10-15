Environment. Python-пакет для развертки окружения БД Postgres в контейнере

**Описание**

Данный пакет предназначен для автоматизированного поднятия контейнера postgres 
с БД на борту. Он пригодится, например, в том случае, если необходимо создать
окружение для проведения unit-тестов, связанных с работой с БД. 
Именно это и стало основной причиной создания пакета Environment

**Установка**

Для установки пакета в интерпретатор Python выполнить команды:
```Bash
pip install poetry
poetry install
```

**Использование**

Внутри пакета находятся два основных модуля для работы с docker-ом и 
файловой системой, комбинируя которые можно создать окружение для своих целей.

### 1. Работа с оберткой над файловой системой (модуль storage)

Модуль storage может быть полезен в случае, если нужно создать временную
папку для поднятия окружения для проведения тестов.

Для создания хранилища нужно передать два аргумента:
- root (корневая папка, где будет храниться временная папка)
- folder_name (папка хранилища)

_Пример создания_:
```python
from environment import Storage

my_storage = Storage(root='/tmp', folder_name='my-tmp-folder')
my_storage.create()
```

_Для физического удаления хранилища с компьютера используется метод clear():_
```python
from environment import Storage

my_storage = Storage(root='/tmp', folder_name='my-tmp-folder')
my_storage.clear()
```

### 2. Работа с кастомным клиентом docker

Модуль docker_client позволяет работать со встроенным docker-клиентом системы
через python.

Для создания объекта CustomDockerClient не требуются входные аргументы

_Пример создания:_

```python
from environment import CustomDockerClient

my_client = CustomDockerClient()
```

_Создание образа:_

```python
my_client.create_image(
    docker_root=dockerfile_root,
    image_name=image_name
)
```

_Запуск контейнера из образа:_

```python
my_client.run_container(
    image_name=image_name,
    environment_vars=['param1:val1', 'param2:val2'],
    ports={'5432/tcp': 8133},
    volumes=['storage/path:my/path'],
    container_name=container_name
)
```

_Удаление контейнера из системы:_

```python
my_client.remove_container(container_name='my-container')
```

_Удаление образа из системы:_

```python
my_client.remove_image(image_name=image_name)
```
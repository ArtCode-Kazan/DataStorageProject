**Описание микросервиса для управления CRUD операциями БД**

- dbase_api_server

    Здесь хранится описание микросервиса с API управления БД. 
    Микросервис основан на FastApi.

- postgres-server

    Здесь хранится SQL-скрипт создания БД Postgres, 
    а также Docker-файл для создания отдельного контейнера с БД.


**Как развернуть пакет на компьютере разработчика**

Достаточно выполнить команду:
``` Bash 
cd <root>/dbase-api-server
poetry install
```

**Как настроить тестовое окружение**

В папке tests нужно создать `.env` файл с такими переменными 
(значения могут быть любыми):
`
POSTGRES_USER=test-account
POSTGRES_PASSWORD=q1w2e3r4t5y6
POSTGRES_DBASE=test-dbase
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=8133
`

<div id="header" align="center">
  <h1>RefSystem API</h1>
  <img src="https://img.shields.io/badge/Python-3.7.9-F8F8FF?style=for-the-badge&logo=python&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/FastAPI-0.103.2-F8F8FF?style=for-the-badge&logo=FastAPI&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/PostgreSQL-555555?style=for-the-badge&logo=postgresql&logoColor=F5F5DC">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0.36-F8F8FF?style=for-the-badge&logo=SQLAlchemy&logoColor=20B2AA">
  <img src="https://img.shields.io/badge/Docker-555555?style=for-the-badge&logo=docker&logoColor=2496ED">
</div>

# Документация API
RefSystem - [API redoc](https://kaschenkkko.github.io/RefSystemAPI/)

# Техническое задание проекта:

Необходимо разработать простой RESTful API сервис для реферальной системы.

# Функциональные требования:
- Регистрация и аутентификация пользователя (JWT, Oauth 2.0).
- Аутентифицированный пользователь должен иметь возможность создать или удалить свой реферальный код.Одновременно может быть активен только 1 код. При создании кода обязательно должен быть задан его срок годности.
- Возможность получения реферального кода по email адресу реферера.
- Возможность регистрации по реферальному коду в 	качестве реферала.
- Получение информации о рефералах по id реферера.
- UI документация (Swagger/ReDoc).


# Запуск проекта:

- Клонируйте репозиторий.
- Перейдите в папку **infra** и создайте в ней файл **.env** с переменными окружения:
  ```
    DB_HOST=db
    DB_PORT=5432
    DB_NAME=postgres
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=password
    JWT_SECRET_KEY=secret_key
  ``` 
- Из папки **infra** запустите docker-compose:
  ```
  ~$ docker-compose up -d --build
  ```
- В контейнере **backend** выполните миграции:
  ```
  ~$ docker-compose exec backend alembic upgrade head
  ```

Документация к API будет доступна по url-адресу [localhost:8000/redoc](http://localhost:8000/redoc)

Админка будет доступна по url-адресу [localhost:8000/admin](http://localhost:8000/admin)

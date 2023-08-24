![example workflow](https://github.com/Gaius-Capito/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Описание проекта: foodgram_project_react

Foodgram - это веб-платформа с функциональным API, предоставляющая удобный 
инструментарий в области продуктов и кулинарных рецептов. Сервис позволяет 
пользователям не только делиться своими кулинарными рецептами и следить за 
публикациями других пользователей, но и создавать списки понравившихся 
рецептов, которые могут быть преобразованы в список 
покупок перед походом в магазин.

## Проект доступен по ссылкам:


- http://158.160.18.25/
- http://158.160.18.25/admin/

### Документация
- http://158.160.18.25/api/docs/

### Стек
Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL, Yandex Cloud


## Запуск проекта через Docker:


- #### Клонировать репозиторий
```
https://github.com/Gaius-Capito/foodgram-project-react.git
```

- #### В директории infra создать файл .env с данными
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='secret key'
```

- #### В директории infra запустить сборку контейнеров
```
docker compose up -d --build
```

- #### Выполнить миграции
```
docker compose exec backend python manage.py migrate
```

- #### Собирать статику
```
docker compose exec backend python manage.py collectstatic --no-input
```

- #### Импортировать ингредиенты
```
docker-compose exec backend python manage.py import_csv
```

Приложение будет доступно в браузере по адресу localhost

- #### Остановить проект
```
docker-compose down
```

#### Разработал


- [@Gaius-Capito](https://github.com/Gaius-Capito)
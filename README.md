# Фудграм

![Main Foodgram workflow](https://github.com/Rufina007/foodgram/actions/workflows/main.yml/badge.svg)

Сайт для публикации рецептов. Можно добавлять рецепты в избранное, подписываться на авторов и формировать список покупок — ингредиенты по всем рецептам в списке суммируются и отдаются файлом.

Проект доступен по адресу: [rufina-foodgram.duckdns.org](https://rufina-foodgram.duckdns.org)

Документация API: [rufina-foodgram.duckdns.org/api/docs/](https://rufina-foodgram.duckdns.org/api/docs/)

# Технологии

- Python
- Django
- Django REST Framework
- Djoser
- PostgreSQL
- Docker / Docker Compose
- Nginx
- GitHub Actions

# Запуск проекта через Docker

1. Клонируй репозиторий:

```
git clone git@github.com:Rufina007/foodgram.git
cd foodgram
```

2. Создай файл `.env` по образцу `.env.example`.

3. Запусти контейнеры:

```
docker compose up -d --build
```

4. Выполни миграции, собери статику и загрузи данные:

```
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
docker compose exec backend python manage.py load_ingredients
docker compose exec backend python manage.py load_tags
docker compose exec backend python manage.py createsuperuser
```

Проект будет доступен на [http://localhost:8000/](http://localhost:8000/), документация API — на `/api/docs/`, админка — на `/admin/`.

Наполнить сайт демо-рецептами:

```
docker compose exec backend python manage.py create_test_data
```

# Запуск бэкенда без Docker

```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py load_ingredients
python manage.py load_tags
python manage.py createsuperuser
python manage.py runserver
```

По умолчанию используется SQLite (`USE_SQLITE=True` в `.env`), поднимать Postgres для этого не нужно.

# CI/CD

Деплой настроен через GitHub Actions (`.github/workflows/main.yml`): проверка PEP8 → сборка и публикация образов backend/frontend/gateway в Docker Hub → деплой на сервер → уведомление в Telegram.

Секреты репозитория: `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `HOST`, `USER`, `SSH_KEY`, `TELEGRAM_TO`, `TELEGRAM_TOKEN`.

# Автор

[Rufina007](https://github.com/Rufina007)

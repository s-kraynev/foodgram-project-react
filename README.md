## Сервер с приложением:
url: https://skr-foodgram.ddns.net
админка:
- login: admin
- password: (фамилия латиницей)

## Проект Foodgram

Пользователи Foodgram могут публиковать рецепты, подписываться на публикации
других пользователей, добавлять понравившиеся рецепты в список «Избранное»,
а перед походом в магазин скачивать сводный список продуктов, необходимых
для приготовления одного или нескольких выбранных блюд. 

Функционал API:
1) Просмотр, создание, редактирование, удаление рецептов блюд.
2) Выбор ингрединтов для блюда из предустановленного списка
3) Выбор при создании рецепта тега и фильтрация по тегам
4) Добавление и удаление рецепта из списка "Избранное"
5) Подписка и удалене подписки на пользователя для просмотра его рецептов
6) Добавление и удаление рецепта в корзину покупок и возможность загрузки PDF файла со списком ингрединтов для блюд в корзине покупок
7) Регистрация, Авторизация, Разлогирование пользователя
8) Смена пароля пользователю

## Стек технологий

[![Python](https://img.shields.io/badge/-Python-464641?-style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-464646?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![Pytest](https://img.shields.io/badge/Pytest-464646?style=flat-square&logo=pytest)](https://docs.pytest.org/en/6.2.x/)
[![Postman](https://img.shields.io/badge/Postman-464646?style=flat-square&logo=postman)](https://www.postman.com/)

## Как запустить проект

Cоздать и активировать виртуальное окружение:

```
cd backend/
python3 -m venv venv
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py makemigrations users ingredients recipes tags
python manage.py migrate

```
Загрузка тестовых данных из csv файлов

```
python manage.py loadcsv ../data
```
(для тестовых пользователь пароль доступа: -)

Создание суперпользователя для доступа к админке

```
python manage.py createsuperuser --email admin@ya.ru --username admin --first_name admin --last_name adminovich
```

Секретный ключ
Храним в файле .env и получаем с помощью команды

```
os.getenv('SECRET_KEY')
Ключ храним в виде  SECRET_KEY='секретный ключ'
```

И не забываем создать файл .env на уровне виртуального окружения
И прописать в нем: SECRET_KEY=<ваш код>

## Запуск тестов
Линтеры:

```
flake8 .
black .
```

Pytest(без тестов на данный момент):
```
pytest
```
## Просмотр API документации
```
python manage.py runserver
# open link:
http://127.0.0.1/api/docs/redoc.html
```
## Примеры работы с API для всех пользователей

Подробная документация доступна по эндпоинту /api/docs/redoc.html

```
Права доступа: Доступно без токена.
GET /api/recipes/ - Получение списка рецептов

Права доступа: Авторизированные пользователи.
GET /api/ingredients/ - Получение списка всех ингредиентов
GET /api/tags/ - Получение списка всех тегов
GET /api/recipes/?page=1&limit=6&is_favorited=1 - Получение списка избранных рецептов
GET /api/recipes/?page=1&limit=6&tags=tag1&tags=tag2 - Получение списка рецептов по тегам
GET /api/recipes/?page=1&limit=999&is_in_shopping_cart=1 - Получение списка рецептов в корзине покупок
GET /api/users/subscriptions - Получение списка авторов на которых подписан пользователь
GET /api/users/ - Получение списка всех пользователей
```

### Локальный запуск проекта
## Без контейнеров с sqlite db

Патчим proxy в файле frontend/package.json
```
"proxy": "http://127.0.0.1:8000/"
```

Собираем UI
```
cd frontend
npm -i
npm run start
```

Меняем posgresql на sqlite в backend/foodgram/settings.py
Запускаем проект по инструкции выше в файле командой
```
python manage.py runserver
```

## В контейнере
Для сборки проекта необходимо установить docker согласно 
[инструкции](https://docs.docker.com/engine/install/ubuntu/).

А также установить docker compose:
```
sudo apt update
sudo apt install docker-compose
```

Запуск локально в контейнере 
(для запуска docker могут потребоваться права root пользователя):
```
cd infra
docker-compose up
# настройка БД
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py loadcsv /load_data
docker compose exec backend python manage.py createsuperuser --email admin@ya.ru --username admin
# настройка статики для админки (volume смонтирован отдельно чтобы не перетирать статику frontend-a)
docker compose exec backend python manage.py collectstatic
docker compose exec backend  cp -r /app/collected_static/. /backend_static/
docker compose exec nginx cp -r /backend_static/. /usr/share/nginx/html/static/.
```

### Важные заметки
- В папке backend находится файл - FreeSans.ttf
  Он необходим в контейнере для корректной работы библиотеки по выгрузке PDF списка покупок.
  Отсутвие файла приводит к ошибке
- Volume c data монтируется в /load_data для запуска миграций тестовых значений

### Автор backend части и деплоя
- :white_check_mark: [s-kraynev](https://github.com/s-kraynev)

TODO:
- add inline logic to recipe admin model
- add pictures for all data
- create admin user on cloud server

## Проект Foodgram

Пользователи Foodgram могут публиковать рецепты, подписываться на публикации
других пользователей, добавлять понравившиеся рецепты в список «Избранное»,
а перед походом в магазин скачивать сводный список продуктов, необходимых
для приготовления одного или нескольких выбранных блюд. 

(TODO)
Функционал API:
1) Просмотр произведений (кино, музыка, книги), которые подразделяются по жанрам и категориям..
2) Возможность оставлять отзывы на произведения и ставить им оценки, на основе которых построена система рейтингов.
3) Комментирование оставленных отзывов.

## Стек технологий

[![Python](https://img.shields.io/badge/-Python-464641?-style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-464646?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![Pytest](https://img.shields.io/badge/Pytest-464646?style=flat-square&logo=pytest)](https://docs.pytest.org/en/6.2.x/)
[![Postman](https://img.shields.io/badge/Postman-464646?style=flat-square&logo=postman)](https://www.postman.com/)

## Как запустить проект

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

(TODO)
Выполнить миграции:

```
python manage.py makemigrations users
python manage.py makemigrations titles
python manage.py migrate users
python manage.py migrate titles
python manage.py migrate

```
(TODO)
Загрузка тестовых данных из csv файлов

```
python manage.py loadcsv ./static/data/
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

Pytest:
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

Для неавторизованных пользователей работа с API доступна в режиме чтения, что-либо изменить или создать не получится.

```
Права доступа: Доступно без токена.
GET /api/v1/categories/ - Получение списка всех категорий
GET /api/v1/genres/ - Получение списка всех жанров
GET /api/v1/titles/ - Получение списка всех произведений
GET /api/v1/titles/{title_id}/reviews/ - Получение списка всех отзывов
GET /api/v1/titles/{title_id}/reviews/{review_id}/comments/ - Получение списка всех комментариев к отзыву
Права доступа: Администратор
GET /api/v1/users/ - Получение списка всех пользователей
```
## Регистрация нового пользователя
Получить код подтверждения на переданный email.
Права доступа: Доступно без токена.
Использовать имя 'me' в качестве username запрещено.
Поля email и username должны быть уникальными.

Регистрация нового пользователя:

```
POST /api/v1/auth/signup/
```

```json
{
  "email": "string",
  "username": "string"
}

```

Получение JWT-токена:

```
POST /api/v1/auth/token/
```

```json
{
  "username": "string",
  "confirmation_code": "string"
}
```

## Примеры работы с API для авторизованных пользователей

Добавление категории:

```
Права доступа: Администратор.
POST /api/v1/categories/
```

```json
{
  "name": "string",
  "slug": "string"
}
```

### Сборка проекта

Для сборки проекта необходимо установить docker согласно 
[инструкции](https://docs.docker.com/engine/install/ubuntu/).

А также установить docker compose:
```
sudo apt update
sudo apt install docker-compose
```

Запуск frontend локально:
```
cd infra
docker-compose up
```

### Авторы
- :white_check_mark: [s-kraynev](https://github.com/s-kraynev)

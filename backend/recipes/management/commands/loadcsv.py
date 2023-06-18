import csv
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    MeasurementUnit,
    Recipe,
    Tag,
    User,
    UsedIngredient,
)

User = get_user_model()


def get_ingredients(data):
    obj_list = []
    units = {}  # name: id
    for idx, row in enumerate(data, start=1):
        row['id'] = idx
        # use custom handling for data with Foreign keys
        unit = row.pop('measure_unit')
        if unit in units:
            row['measurement_unit'] = MeasurementUnit.objects.get(
                id=units[unit]
            )
        else:
            units[unit] = len(units) + 1
            row['measurement_unit'] = MeasurementUnit.objects.create(
                id=units[unit],
                unit=unit,
            )
        obj_list.append(Ingredient(**row))
    Ingredient.objects.bulk_create(obj_list)


def get_tags(data):
    obj_list = [Tag(**row) for row in data]
    Tag.objects.bulk_create(obj_list)


def get_users(data):
    obj_list = [User(**row) for row in data]
    User.objects.bulk_create(obj_list)


def get_follows(data):
    users = {}  # id: user
    obj_list = []
    for row in data:
        for key in ('author', 'user'):
            user_id = row[key]
            if user_id not in users:
                users[user_id] = User.objects.get(id=user_id)
            row[key] = users[user_id]
        obj_list.append(Follow(**row))
    Follow.objects.bulk_create(obj_list)


def get_recipes(data):
    users = {}  # id: user
    tags = {}  # id: tag
    for row in data:
        user_id = row['author']
        if user_id not in users:
            users[user_id] = User.objects.get(id=user_id)
        row['author'] = users[user_id]

        tag_ids = row.pop('tags', '').split(';')
        ingredients = row.pop('ingredients').split(';')
        created_recipe = Recipe.objects.create(**row)

        for tag_id in tag_ids:
            if tag_id not in tags:
                tags[tag_id] = Tag.objects.get(id=tag_id)
            created_recipe.tags.add(tags[tag_id])

        for ingr in ingredients:
            ingredient_id, amount = ingr.split('-')
            ingr_data = {
                'ingredient': Ingredient.objects.get(id=ingredient_id),
                'amount': amount,
            }
            used_ingredient = UsedIngredient.objects.create(**ingr_data)
            created_recipe.ingredients.add(used_ingredient)


def get_favorites(data):
    users = {}  # id: user
    recipes = {}  # id: recipe
    obj_list = []
    for row in data:
        user_id = row['user']
        if user_id not in users:
            users[user_id] = User.objects.get(id=user_id)
        row['user'] = users[user_id]

        recipe_id = row['recipe']
        if recipe_id not in recipes:
            recipes[recipe_id] = Recipe.objects.get(id=recipe_id)
        row['recipe'] = recipes[recipe_id]

        obj_list.append(Favorite(**row))

    Favorite.objects.bulk_create(obj_list)


FILE_TO_METHOD_MAP = [
    ('ingredients', get_ingredients),
    ('tags', get_tags),
    ('users', get_users),
    ('follows', get_follows),
    ('recipes', get_recipes),
    ('favorites', get_favorites),
]


def load_data_from_csv(f_name, load_func, inst, csv_dir, errors):
    # load ingredients
    f_path = f'{csv_dir}/{f_name}.csv'
    if not os.path.exists(f_path):
        inst.stdout.write(
            inst.style.ERROR(
                f'Ожидаемый файл {f_name}.csv не был найден в директории '
                f'{csv_dir}. Загрузка данных из него не выполнена.'
            )
        )
    with open(f_path, newline='', encoding="utf-8") as csvfile:
        try:
            data = csv.DictReader(csvfile, delimiter=',')
            load_func(data)
        except Exception as exc:
            errors.append(
                f'Во время загрузки из файла {f_name}.csv возникла '
                f'ошибка: {exc}'
            )


def load_data_from_all_csv_files(inst, csv_dir, errors):
    for f_name, method in FILE_TO_METHOD_MAP:
        load_data_from_csv(f_name, method, inst, csv_dir, errors)


class Command(BaseCommand):
    help = 'Upload csv data to existed DB'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_dir_path', type=str, help='Путь до директории с csv файлами'
        )

    def handle(self, *args, **options):
        csv_dir = options['csv_dir_path']
        if not os.path.exists(csv_dir):
            raise CommandError(
                f'Директория {csv_dir} не была найдена. '
                'Попробуйте указать другой путь.'
            )
        errors = []
        load_data_from_all_csv_files(self, csv_dir, errors)
        if errors:
            raise CommandError('\n'.join(errors))
        self.stdout.write(
            self.style.SUCCESS('Загрузка данных завершена успешно')
        )

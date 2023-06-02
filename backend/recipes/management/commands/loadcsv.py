import csv
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient, MeasurementUnit

User = get_user_model()


def load_data_from_csv(inst, csv_dir, errors):
    # load ingredients
    f_name = 'ingredients'
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
        except Exception as exc:
            errors.append(
                f'Во время загрузки из файла {f_name}.csv возникла '
                f'ошибка: {exc}'
            )


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
        load_data_from_csv(self, csv_dir, errors)
        if errors:
            raise CommandError('\n'.join(errors))
        self.stdout.write(
            self.style.SUCCESS('Загрузка данных завершена успешно')
        )

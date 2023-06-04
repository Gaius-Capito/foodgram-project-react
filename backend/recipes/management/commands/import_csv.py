import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Команда import_csv добавляет данные в базу данных из csv файлов.'

    def handle(self, *args, **options):
        csv_file = Path(settings.BASE_DIR)/'data'/'ingredients.csv'
        if not csv_file.exists():
            raise CommandError(f'Файл {csv_file} не существует.')

        upload_list = []
        with open(csv_file, 'r', encoding='utf-8') as ing_file:
            reader = csv.reader(ing_file, delimiter=',')
            for row in reader:
                name, measurement_unit = row
                new_data = Ingredient(
                    name=name,
                    measurement_unit=measurement_unit)
                if new_data not in upload_list:
                    upload_list.append(new_data)
            Ingredient.objects.bulk_create(upload_list)
            self.stdout.write(
                self.style.SUCCESS('Данные успешно загружены'))


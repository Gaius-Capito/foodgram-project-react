import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Команда import_csv добавляет данные в базу данных из csv файлов.'

    def handle(self, *args, **options):
        csv_ingredients = Path(settings.BASE_DIR) / 'data' / 'ingredients.csv'
        csv_tags = Path(settings.BASE_DIR) / 'data' / 'tags.csv'
        if not csv_ingredients.exists():
            raise CommandError(f'Файл csv_ingredients не существует.')

        with open(csv_ingredients, 'r', encoding='utf-8') as ing_file:
            reader = csv.reader(ing_file, delimiter=',')
            for row in reader:
                name, measurement_unit = row
                ingredient, created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )

                if not created:
                    self.stdout.write(self.style.WARNING(
                        f'Ингредиент {ingredient.name} уже существует.'))
            self.stdout.write(
                self.style.SUCCESS('Ингредиенты успешно загружены'))

        if not csv_tags.exists():
            raise CommandError(f'Файл csv_tags не существует.')

        with open(csv_tags, 'r', encoding='utf-8') as ing_file:
            reader = csv.reader(ing_file, delimiter=',')
            for row in reader:
                name, slug, color = row
                tag, created = Tag.objects.get_or_create(
                    name=name,
                    slug=slug,
                    color=color
                )

                if not created:
                    self.stdout.write(self.style.WARNING(
                        f'Тег {tag.name} уже существует.'))
            self.stdout.write(
                self.style.SUCCESS('Теги успешно загружены'))

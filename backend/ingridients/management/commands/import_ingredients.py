import csv
import os

from django.core.management.base import BaseCommand
from ingridients.models import Ingredient
from django.conf import settings


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из CSV-файла'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'data/ingredients.csv')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл не найден: {file_path}'))
            return

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            added = 0
            skipped = 0
            for row in reader:
                name = row['name']
                unit = row['measurement_unit']
                obj, created = Ingredient.objects.get_or_create(
                    name=name, measurement_unit=unit
                )
                if created:
                    added += 1
                else:
                    skipped += 1
        self.stdout.write(
            self.style.SUCCESS(
                f'Импорт завершён: добавлено {added}, пропущено {skipped}.'
            )
        )

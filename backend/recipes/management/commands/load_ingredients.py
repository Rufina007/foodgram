import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

INGREDIENTS_FILE_PATH = settings.BASE_DIR / 'data' / 'ingredients.json'


class Command(BaseCommand):
    help = 'Загружает список ингредиентов из data/ingredients.json.'

    def handle(self, *args, **options):
        with open(INGREDIENTS_FILE_PATH, encoding='utf-8') as file:
            data = json.load(file)

        ingredients = [Ingredient(**item) for item in data]
        Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(
            f'Обработано ингредиентов: {len(data)}.',
        ))

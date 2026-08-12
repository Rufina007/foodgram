import json

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает список ингредиентов из data/ingredients.json.'

    def handle(self, *args, **options):
        path = settings.BASE_DIR / 'data' / 'ingredients.json'
        with open(path, encoding='utf-8') as file:
            data = json.load(file)

        ingredients = [Ingredient(**item) for item in data]
        Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(
            f'Обработано ингредиентов: {len(data)}.',
        ))

import io
import json
import random

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import BaseCommand
from PIL import Image

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User

DEMO_DATA_FILE_PATH = settings.BASE_DIR / 'data' / 'demo_data.json'
PLACEHOLDER_COLORS = (
    (239, 108, 0), (67, 160, 71), (30, 136, 229), (142, 36, 170),
    (0, 151, 167), (216, 27, 96), (93, 64, 55), (97, 97, 97),
)
PLACEHOLDER_SIZE = (400, 300)
RECIPE_TAGS_COUNT = 2
RECIPE_INGREDIENTS_COUNT = 3
MIN_DEMO_AMOUNT = 1
MAX_DEMO_AMOUNT = 500


def build_placeholder_image(color, filename):
    buffer = io.BytesIO()
    Image.new('RGB', PLACEHOLDER_SIZE, color).save(buffer, format='JPEG')
    return ContentFile(buffer.getvalue(), name=filename)


class Command(BaseCommand):
    help = (
        'Создаёт демо-пользователей и рецепты из data/demo_data.json — '
        'для проверки работы проекта на тестовых данных.'
    )

    def handle(self, *args, **options):
        if not Tag.objects.exists():
            call_command('load_tags')
        if not Ingredient.objects.exists():
            call_command('load_ingredients')

        tags = list(Tag.objects.all())
        ingredients = list(Ingredient.objects.all())
        if not ingredients:
            self.stderr.write(self.style.ERROR(
                'В базе нет ингредиентов, наполнение рецептов невозможно.',
            ))
            return

        with open(DEMO_DATA_FILE_PATH, encoding='utf-8') as file:
            demo_users = json.load(file)['users']

        image_index = 0
        for user_data in demo_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                },
            )
            if created:
                user.set_password(user_data['password'])
                user.save()

            for recipe_data in user_data['recipes']:
                if Recipe.objects.filter(
                    author=user, name=recipe_data['name'],
                ).exists():
                    continue

                image = build_placeholder_image(
                    PLACEHOLDER_COLORS[image_index % len(PLACEHOLDER_COLORS)],
                    f'{user.username}_{image_index}.jpg',
                )
                image_index += 1
                recipe = Recipe.objects.create(
                    author=user,
                    image=image,
                    name=recipe_data['name'],
                    text=recipe_data['text'],
                    cooking_time=recipe_data['cooking_time'],
                )
                recipe.tags.set(
                    random.sample(tags, k=min(RECIPE_TAGS_COUNT, len(tags))),
                )
                RecipeIngredient.objects.bulk_create(
                    RecipeIngredient(
                        recipe=recipe,
                        ingredient=ingredient,
                        amount=random.randint(
                            MIN_DEMO_AMOUNT, MAX_DEMO_AMOUNT,
                        ),
                    )
                    for ingredient in random.sample(
                        ingredients,
                        k=min(RECIPE_INGREDIENTS_COUNT, len(ingredients)),
                    )
                )

        self.stdout.write(self.style.SUCCESS(
            'Демо-пользователи и рецепты готовы (пароль каждого — '
            'DemoPass123, задан в data/demo_data.json).',
        ))

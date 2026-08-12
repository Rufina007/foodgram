import io
import random

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import BaseCommand
from PIL import Image

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User

DEMO_USERS = (
    {
        'username': 'demo_anna',
        'email': 'demo.anna@foodgram.example',
        'first_name': 'Анна',
        'last_name': 'Демидова',
        'password': 'DemoPass123',
    },
    {
        'username': 'demo_igor',
        'email': 'demo.igor@foodgram.example',
        'first_name': 'Игорь',
        'last_name': 'Сорокин',
        'password': 'DemoPass123',
    },
    {
        'username': 'demo_olga',
        'email': 'demo.olga@foodgram.example',
        'first_name': 'Ольга',
        'last_name': 'Куликова',
        'password': 'DemoPass123',
    },
)

DEMO_RECIPES = (
    {
        'name': 'Овсянка с ягодами',
        'text': 'Сварите овсянку на молоке, добавьте свежие ягоды и мёд.',
        'cooking_time': 15,
    },
    {
        'name': 'Салат с авокадо и креветками',
        'text': (
            'Смешайте отварные креветки, нарезанный авокадо, черри и зелень,'
            ' заправьте оливковым маслом.'
        ),
        'cooking_time': 20,
    },
    {
        'name': 'Тыквенный суп-пюре',
        'text': (
            'Обжарьте лук, добавьте тыкву и бульон, варите до готовности '
            'и пробейте блендером.'
        ),
        'cooking_time': 40,
    },
)

PLACEHOLDER_COLORS = ((239, 108, 0), (67, 160, 71), (30, 136, 229))


def build_placeholder_image(color, filename):
    buffer = io.BytesIO()
    Image.new('RGB', (400, 300), color).save(buffer, format='JPEG')
    return ContentFile(buffer.getvalue(), name=filename)


class Command(BaseCommand):
    help = (
        'Создаёт демо-пользователей и по одному рецепту на каждого — '
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

        for index, user_data in enumerate(DEMO_USERS):
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

            recipe_data = DEMO_RECIPES[index % len(DEMO_RECIPES)]
            if Recipe.objects.filter(
                author=user, name=recipe_data['name'],
            ).exists():
                continue

            image = build_placeholder_image(
                PLACEHOLDER_COLORS[index % len(PLACEHOLDER_COLORS)],
                f'{user.username}.jpg',
            )
            recipe = Recipe.objects.create(
                author=user,
                image=image,
                **recipe_data,
            )
            recipe.tags.set(random.sample(tags, k=min(2, len(tags))))
            RecipeIngredient.objects.bulk_create(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=random.randint(1, 500),
                )
                for ingredient in random.sample(
                    ingredients, k=min(3, len(ingredients)),
                )
            )

        self.stdout.write(self.style.SUCCESS(
            'Демо-пользователи и рецепты готовы (пароль каждого — '
            'DemoPass123, задан прямо в этой команде).',
        ))

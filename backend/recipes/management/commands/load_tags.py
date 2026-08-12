from django.core.management.base import BaseCommand

from recipes.models import Tag

DEFAULT_TAGS = (
    ('Завтрак', 'breakfast'),
    ('Обед', 'lunch'),
    ('Ужин', 'dinner'),
)


class Command(BaseCommand):
    help = 'Создаёт стартовый набор тегов.'

    def handle(self, *args, **options):
        tags = [Tag(name=name, slug=slug) for name, slug in DEFAULT_TAGS]
        Tag.objects.bulk_create(tags, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(
            f'Обработано тегов: {len(tags)}.',
        ))

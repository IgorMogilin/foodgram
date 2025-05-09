from autoslug import AutoSlugField
from django.db import models
from unidecode import unidecode

from backend.constants import TAG_MAX_LENGTH_NAME, TAG_SLUG_MAX_LENGTH


def transliterate_to_slug(text):
    """Явно объявленная функция для slugify"""
    return unidecode(text).lower().replace(' ', '-')


class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_MAX_LENGTH_NAME,
        unique=True,
        verbose_name="Название тега"
    )
    slug = AutoSlugField(
        populate_from='name',
        unique=True,
        slugify=transliterate_to_slug,
        max_length=TAG_SLUG_MAX_LENGTH,
        editable=False,
        verbose_name="Слаг тега"
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name

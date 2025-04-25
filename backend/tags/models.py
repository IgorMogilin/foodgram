from autoslug import AutoSlugField
from django.db import models
from unidecode import unidecode


def custom_slugify(text):
    """Явно объявленная функция для slugify"""
    return unidecode(text).lower().replace(' ', '-')


class Tag(models.Model):
    name = models.CharField(
        max_length=32,
        unique=True,
        verbose_name="Название тега"
    )
    slug = AutoSlugField(
        populate_from='name',
        unique=True,
        slugify=custom_slugify,
        max_length=32,
        editable=False,
        verbose_name="Слаг тега"
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name

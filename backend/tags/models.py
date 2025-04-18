from django.db import models
from autoslug.fields import AutoSlugField
from unidecode import unidecode


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)
    slug = AutoSlugField(
        populate_from='name',
        unique=True,
        slugify=lambda x: unidecode(x).lower().replace(' ', '-'),
        max_length=32,
        editable=False,
    )

    def __str__(self):
        return self.name

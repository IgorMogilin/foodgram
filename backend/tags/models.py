from django.db import models
from autoslug.fields import AutoSlugField


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True)
    slug = AutoSlugField(
        populate_from="name",
        unique=True,
        max_length=32,
        allow_unicode=False,
        editable=False,
    )

    def __str__(self):
        return self.name

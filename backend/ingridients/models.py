from api.constants import (
    INGREDIENT_MAX_LENGTH_NAME,
    MAX_LENGTH_MEASUREMENT_UNIT
)
from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=INGREDIENT_MAX_LENGTH_NAME)
    measurement_unit = models.CharField(max_length=MAX_LENGTH_MEASUREMENT_UNIT)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

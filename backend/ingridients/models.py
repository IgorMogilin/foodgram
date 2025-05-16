from django.db import models

from api.constants import (
    INGREDIENT_MAX_LENGTH_NAME,
    MAX_LENGTH_MEASUREMENT_UNIT,
)


class Ingredient(models.Model):
    name = models.CharField(max_length=INGREDIENT_MAX_LENGTH_NAME)
    measurement_unit = models.CharField(max_length=MAX_LENGTH_MEASUREMENT_UNIT)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_name_measurement'
            )
        ]

        def str(self):
            return f"{self.name} ({self.measurement_unit})"

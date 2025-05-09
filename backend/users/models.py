from django.contrib.auth.models import AbstractUser
from django.db import models

from ..constants import (
    USER_FIRSTNAME_MAX_LENGTH,
    USER_LASTNAME_MAX_LENGTH
)


class User(AbstractUser):
    email = models.EmailField(
        'Email',
        unique=True,
        error_messages={"unique": "Пользователь с таким email уже существует."}
    )
    first_name = models.CharField('Имя', max_length=USER_FIRSTNAME_MAX_LENGTH)
    last_name = models.CharField(
        'Фамилия',
        max_length=USER_LASTNAME_MAX_LENGTH
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Аватар'
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='no_self_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'

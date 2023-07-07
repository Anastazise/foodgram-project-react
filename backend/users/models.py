from django.contrib.auth.models import AbstractUser

from django.db import models

from django.db.models import UniqueConstraint
from django.db.models import CharField, EmailField

from django.conf import settings


class User(AbstractUser):
    email = EmailField(
        verbose_name='Адрес электронной почты',
        max_length=settings.MAX_NAME_LENGTH,
        unique=True,
        help_text='Введите Email',
    )
    username = CharField(
        verbose_name='Уникальный никнейм',
        max_length=settings.MAX_NAME_LENGTH,
        unique=True,
        help_text='Придумайте имя пользователя',
    )
    first_name = CharField(
        verbose_name='Имя',
        max_length=settings.MAX_NAME_LENGTH,
        help_text='Укажите имя',
    )
    last_name = CharField(
        verbose_name='Фамилия',
        max_length=settings.MAX_NAME_LENGTH,
        help_text='Укажите фамилию',
    )
    password = CharField(
        verbose_name=('Пароль'),
        max_length=settings.MAX_NAME_LENGTH,
        help_text='Придумайте пароль',
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        related_name='subscriber',
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='subscribing',
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-user']
        constraints = [
            UniqueConstraint(fields=['user', 'author'],
                             name='unique_subscription')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Пользователь {self.user} -> автор {self.author}'

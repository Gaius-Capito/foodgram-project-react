from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from api.validators import validate_real_name
from recipes import constants


class User(AbstractUser):
    username = models.CharField(
        'Логин',
        max_length=constants.LENGTH_OF_FIELDS_USER,
        unique=True,
        validators=[UnicodeUsernameValidator]
    )
    first_name = models.CharField(
        'Имя',
        max_length=constants.LENGTH_OF_FIELDS_USER,
        validators=[validate_real_name]
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=constants.LENGTH_OF_FIELDS_USER,
        validators=[validate_real_name]
    )
    password = models.CharField(
        'Пароль',
        max_length=constants.LENGTH_OF_FIELDS_USER
    )
    email = models.EmailField(
        'Email',
        max_length=constants.LENGTH_OF_USER_EMAIL,
        unique=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author'
    )

    class Meta:
        ordering = ('-author_id',)
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_user_author'),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='not_subscribe_youerself'
            )]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'

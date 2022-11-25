from core.models import PubDateModel
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.settings import ADMIN, MODERATOR, USER

from .validators import year_validator

CHOICES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class User(AbstractUser):
    bio = models.CharField('О себе', max_length=250, null=True, blank=True)
    role = models.CharField(
        'Роль',
        max_length=20,
        default='user',
        choices=CHOICES
    )
    confirmation_code = models.CharField(
        'Код подтверждения аутентификации',
        max_length=10,
        null=True,
        blank=True
    )
    email = models.EmailField('Почтовый ящик', unique=True)


class Genre(models.Model):
    name = models.CharField('Название жанра', max_length=100)
    slug = models.SlugField('Уникальный идентификатор жанра', unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField('Название категории', max_length=256)
    slug = models.SlugField(
        'Уникальный идентификатор категории',
        unique=True,
        max_length=50
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    name = models.CharField('Название произведения', max_length=100)
    year = models.IntegerField('Год создания', validators=[year_validator])
    description = models.TextField(
        'Описание произведения',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenreAssign',
        related_name='title',
        verbose_name='Жанр произведения',
        blank=True
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        related_name='title',
        verbose_name='Категория произведения'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['-year']

    @property
    def rating(self):
        reviews = Review.objects.filter(title=self.pk)
        scores = 0
        count = 0
        for review in reviews:
            scores += review.score
            count += 1
        if count == 0:
            return None
        return scores / count
    rating.fget.shor_description = 'Рейтинг'

    def __str__(self):
        return self.name[0:15]


class Review(PubDateModel):
    author = models.ForeignKey(
        User,
        verbose_name='Автор обзора',
        on_delete=models.CASCADE,
        related_name='review'
    )
    text = models.TextField(
        verbose_name='Обзор',
        max_length=100,
        help_text='Напишите ваш отзыв'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10))
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique_title_author'
            ),
        )

    def __str__(self):
        return self.text[0:15]


class Comment(PubDateModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Обзор'
    )
    text = models.TextField('Текст комментария', max_length=500)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[0:15]


class TitleGenreAssign(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )

    class Meta:
        unique_together = (('title', 'genre'),)

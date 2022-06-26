from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Описание")

    def __str__(self) -> str:
        return f'Группа {self.title}'

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст поста",
        help_text='Напишите что-то важное')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор"
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name="Группа",
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"


class Comment(models.Model):
    text = models.TextField(
        verbose_name="Текст комментария",
        help_text='Напишите что-то без мата )'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Автор"
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='comments',
        verbose_name="Пост ",
    )

    def __str__(self) -> str:
        return f'Группа {self.title}'

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name='follower',
        help_text='Кто подписан'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Автор",
        help_text='На кого подписан'
    )

    def __str__(self) -> str:
        return f'Пользователь {self.user} подписан на {self.author}'

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                name='unique_follows',
                fields=['user', 'author'],
            ),
        ]

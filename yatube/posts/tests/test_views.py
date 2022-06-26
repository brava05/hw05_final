from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from posts.models import Post, Group, Comment, Follow
from posts.forms import PostForm
from django.conf import settings
from django.core.cache import caches


User = get_user_model()


class TaskPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создаем пользователя
        cls.user = User.objects.create_user(username='post_author_view')

        cls.test_group_for_post = Group.objects.create(
            title='Группа для теста нового поста',
            slug='group_for_post')

        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.test_group
        )

        cls.number_of_general_posts = Post.objects.count()

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache = caches['default']
        cache.clear()

    def checking_context(self, post_1, post_2):
        self.assertEqual(post_1.group, post_2.group)
        self.assertEqual(post_1.text, post_2.text)
        self.assertEqual(post_1.author, post_2.author)
        self.assertEqual(post_1.pub_date, post_2.pub_date)
        self.assertEqual(post_1.image, post_2.image)

    # Проверка словаря контекста главной страницы
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""

        response = (self.authorized_client.get(reverse('posts:index')))

        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        post = Post.objects.first()

        first_object = response.context['page_obj'][0]
        self.checking_context(first_object, post)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""

        response = (self.authorized_client.
                    get(reverse('posts:group_list', kwargs={'slug': 'slug'})))

        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        self.checking_context(first_object, self.post)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""

        response = (self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'post_author_view'})
        ))

        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        self.checking_context(first_object, self.post)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (
            self.authorized_client.get(
                reverse(
                    'posts:post_detail', kwargs={'post_id': str(self.post.pk)}
                )
            )
        )
        context_post = response.context['post']
        self.assertEqual(context_post, self.post)

    def test_post_edit_pages_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})))
        context_post_id = response.context['post_id']
        self.assertEqual(context_post_id, self.post.pk)

        # проверяем что в контексте есть is_edit и он булево
        self.assertIn('is_edit', response.context)

        context_is_edit = response.context['is_edit']
        self.assertIsInstance(context_is_edit, bool)

        # Проверка элементов формы post_edit
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        # Проверяем, что типы полей формы соответствуют ожиданиям
        response_form = response.context.get('form')
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response_form.fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertIsInstance(response_form, PostForm)

    def test_post_create_pages_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:post_create')))
        # Проверка элементов формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        # Проверяем, что типы полей формы соответствуют ожиданиям
        response_form = response.context.get('form')
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response_form.fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertIsInstance(response_form, PostForm)

    def test_paginator(self):

        posts_count = 13
        posts_list = [Post
                      (
                          text='Тестовый текст ' + str(i),
                          author=self.user,
                          group=self.test_group
                      )
                      for i in range(0, posts_count)]

        Post.objects.bulk_create(posts_list)

        response = (self.authorized_client.get(reverse('posts:index')))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(
            len(response.context['page_obj']), settings.NUMBER_OF_POSTS)

        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         posts_count
                         + self.number_of_general_posts
                         - settings.NUMBER_OF_POSTS
                         )

    def test_new_post_on_index_page(self):
        """Новый пост должен появляться на главной странице."""

        Post.objects.create(
            author=self.user,
            text='Тестовый пост на главной')

        response = (self.authorized_client.get(reverse('posts:index')))

        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый пост на главной')

    def test_new_post_on_group_page(self):
        """Новый пост должен появляться на странице группы."""

        new_post = Post.objects.create(
            author=self.user,
            group=self.test_group_for_post,
            text='Тестовый пост в группе')

        response = (
            self.authorized_client.get(
                reverse(
                    'posts:group_list',
                    kwargs={'slug': 'group_for_post'}
                )
            )
        )

        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым

        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group, new_post.group)
        self.assertEqual(first_object.pk, new_post.pk)
        self.assertEqual(first_object.text, 'Тестовый пост в группе')

    def test_new_post_not_on_wrong_group_page(self):
        """Новый пост не должен появляться на странице другой группы."""

        post = Post.objects.create(
            author=self.user,
            group=self.test_group_for_post,
            text='Тестовый пост в группе')

        response = (self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'slug'})))

        first_object = response.context['page_obj'][0]
        self.assertNotEquals(first_object.pk, post.pk)

    def test_comment_on_post_page(self):
        """После успешной отправки комментарий появляется на странице поста."""

        Comment.objects.create(
            author=self.user,
            post=self.post,
            text='Тестовый коммент')

        response = (
            self.authorized_client.get(
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': str(self.post.pk)}
                )
            )
        )

        # Теперь контест не содержит коментов
        # получаем из поста комент
        first_object = response.context['post'].comments.first()
        self.assertEqual(first_object.text, 'Тестовый коммент')

    def test_cache_index_page(self):
        """Проверка кеширования главной страницы"""
        response_before = self.authorized_client.get(reverse('posts:index'))
        self.post_second = Post.objects.create(
            text='Тестовый 2',
            author=self.user,
        )
        # без чистки кеша контент остался тот-же
        response_after = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_before.content, response_after.content)

        # после чистки кеша контент новый
        cache = caches['default']
        cache.clear()
        response_after_clear = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(
            response_before.content,
            response_after_clear.content
        )

    def test_new_post_on_follow_page(self):
        """Новый пост должен появляться на главной у тех, кто подписан.
        И не появляться у тех, кто не подписан"""

        author_for_follow = User.objects.create_user(
            username='author_for_follow'
        )
        Follow.objects.create(
            user=self.user,
            author=author_for_follow
        )

        Post.objects.create(
            author=author_for_follow,
            text='Тестовый пост для пописчиков')

        response = (
            self.authorized_client.get(
                reverse(
                    'posts:follow_index'
                )
            )
        )

        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый пост для пописчиков')

        # создаем неподписанного пользователя для проверки,
        # что он не видит этот пост
        user_not_follower = User.objects.create_user(
            username='user_not_follower'
        )
        self.not_follower_client = Client()
        self.not_follower_client.force_login(user_not_follower)

        response = (
            self.not_follower_client.get(
                reverse(
                    'posts:follow_index'
                )
            )
        )
        self.assertEqual(len(response.context['page_obj']), 0)

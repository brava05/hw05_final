from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Group, Post
from http import HTTPStatus
from django.urls import reverse

User = get_user_model()


class TaskURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        cls.user = User.objects.create_user(username='post_author')
        Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )

    def setUp(self):
        # Не авторизованный пользователь.
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем несуществующую страницы
    def test_url_not_exists(self):
        """Страница отсутсвует."""

        response = self.guest_client.get('unexisting_page')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    # Проверяем общедоступные страницы
    def test_url_exists_anonymous(self):
        """Страница / доступна любому пользователю."""

        urls_for_all = (
            '/',
            '/group/test-slug/',
            '/profile/post_author/',
            '/posts/1/',
        )
        for url in urls_for_all:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_create_url_exists(self):
        """Страница /post_create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.client.get(reverse('posts:post_create'), follow=True)
        self.assertRedirects(
            response, f'{reverse("users:login")}?next=/create/')

    def test_urls_uses_correct_template(self):
        post = Post.objects.first()
        templates_url_names = (
            ('posts/index.html', '/'),
            ('posts/group_list.html', '/group/test-slug/'),
            ('posts/profile.html', '/profile/post_author/'),
            ('posts/post_detail.html', f'/posts/{str(post.pk)}/'),
            ('posts/create_post.html', '/create/')
        )
        for element in templates_url_names:
            template, address = element
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

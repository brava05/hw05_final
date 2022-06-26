import shutil
import tempfile
from django.contrib.auth import get_user_model
from posts.models import Post, Group, Follow
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.core.cache import caches


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='slug'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='post_author_form')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache = caches['default']
        cache.clear()

    def test_create_post(self):
        """Валидная форма создает запись."""

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст формы',
            'group': self.test_group.id,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': 'post_author_form'}
            )
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), 1)
        # Проверяем, что создалась запись с заданным текстом
        post_after = Post.objects.first()
        self.assertEqual(post_after.text, 'Тестовый текст формы')
        self.assertEqual(post_after.author, self.user)
        self.assertEqual(post_after.group, self.test_group)
        self.assertEqual(post_after.image, 'posts/small.gif')

    def test_post_edit(self):
        """Валидная форма редактирует запись."""

        # Создаем запись в базе данных
        Post.objects.create(
            text='Тестовый текст',
            group=self.test_group,
            author=self.user
        )

        post = Post.objects.first()
        form_data = {
            'text': 'Новый текст формы',
            'group': self.test_group.id,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': post.pk})
        )
        # Проверяем, изменился ли текст нужного поста
        post_after = Post.objects.first()
        self.assertEqual(post_after.text, 'Новый текст формы')

        # Проверяем, что остальные данные не изменились
        self.assertEqual(post_after.group, post.group)
        self.assertEqual(post_after.author, post.author)

        # Проверяем, что пост единственный
        self.assertEqual(Post.objects.count(), 1)

    def test_create_post_for_not_autorised(self):
        """Проверяем отсутствие доступа у неавторизованного клиента."""

        self.guest_client = Client()
        response = self.guest_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response,
                             reverse('users:login') + '?next=/create/'
                             )

    def test_comment_post_for_not_autorised(self):
        """Проверяем отсутствие доступа для комментариев
        у неавторизованного клиента."""

        self.guest_client = Client()

        # Создаем запись для комента в базе данных
        Post.objects.create(
            text='Тестовый текст',
            group=self.test_group,
            author=self.user
        )
        post = Post.objects.first()

        response = self.guest_client.get(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post.pk}
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_following(self):
        """Создаем подписку на автора."""

        author_for_follow = User.objects.create_user(
            username='author_for_follow'
        )
        form_data = {
            'user': self.user,
            'author': author_for_follow,
        }
        # Отправляем POST-запрос
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': 'author_for_follow'}
            ),
            data=form_data,
            follow=True
        )

        # Проверяем, увеличилось ли число подписок
        self.assertEqual(Follow.objects.count(), 1)
        # Проверяем, что создалась подписка именно на этого автора
        follow_after = Follow.objects.first()
        self.assertEqual(follow_after.user, self.user)
        self.assertEqual(follow_after.author, author_for_follow)

        # пытаемся отписаться
        self.authorized_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': 'author_for_follow'}
            ),
            data=form_data,
            follow=True
        )

        # Проверяем, что подписка удалилась
        self.assertEqual(Follow.objects.count(), 0)

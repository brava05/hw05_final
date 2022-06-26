from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост 123456789',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        instances = (
            (self.group, 'Группа ' + self.group.title),
            (self.post, self.post.text[:15]),
        )

        for instance, expected_name in instances:
            with self.subTest(instance=instance):
                self.assertEqual(str(instance), expected_name)

    def test_group_have_correct_object_names(self):
        """Проверяем, что у group корректно работает __str__."""
        expected_object_name = str(self.group)
        self.assertEqual(expected_object_name, 'Группа ' + self.group.title)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verbose_name = (
            ('pub_date', 'Дата публикации'),
            ('text', 'Текст поста'),
            ('author', 'Автор'),
            ('group', 'Группа'),
        )
        for element in field_verbose_name:
            field, expected_value = element
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = (
            ('group', 'Выберите группу'),
            ('text', 'Напишите что-то важное'),
        )
        for element in field_help_texts:
            field, expected_value = element
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

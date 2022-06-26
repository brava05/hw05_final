from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


class StaticPagesURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов """
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

        url_names = ('about:author', 'about:tech')

        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблона для адресов """

        templates_url_names = (
            ('about/author.html', '/about/author/'),
            ('about/tech.html', '/about/tech/'),
        )
        for element in templates_url_names:
            template, address = element
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

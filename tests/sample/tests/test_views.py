import re

from django.urls import reverse
from django.test import Client, TestCase
from django.contrib.auth.models import User

from model_bakery import baker


def get_data_url(response):
    """
    Returns the url contained in the data-ajax attribute from the
    response html content.
    """

    matches = re.search("url\": \\'(.*?)'", response.content.decode('utf-8'), re.S | re.M)
    if not matches:
        return ''

    return matches.group(1)


class TestViews(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestViews, cls).setUpClass()
        cls.client = Client()

    def get_datatable(self, response):
        """
        Gets the datatable contents and returns as a python dict
        """
        response = self.client.get(get_data_url(response))
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_employee_list(self):
        response = self.client.get(reverse('employee_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Birthday")

        # Fetch the ajax
        # Should be empty
        datatable = self.get_datatable(response)
        self.assertEqual(datatable['recordsTotal'], 0)
        self.assertEqual(datatable['data'], [])

        # Add an object
        baker.make('sample.Employee', _quantity=3)

        # Fetch the ajax
        # Should be have somethin'
        datatable = self.get_datatable(response)
        self.assertEqual(datatable['recordsTotal'], 3)

    def test_secure_employee_list(self):
        response = self.client.get(reverse('secure_employee_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Birthday")

        # Fetch the ajax
        # Should be prohibited
        failed_response = self.client.get(get_data_url(response))
        self.assertEqual(failed_response.status_code, 302)

        # Login
        user = User.objects.create_user(
            username='test', email='test@test.com', password='test',
        )
        self.client.login(username=user, password='test')

        # Add an object
        baker.make(
            'sample.Employee',
            first_name="Fred",
            _quantity=3
        )

        # Fetch the ajax
        # Should be have somethin'
        datatable = self.get_datatable(response)
        self.assertEqual(datatable['recordsTotal'], 3)

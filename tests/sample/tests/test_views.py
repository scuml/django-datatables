import json
import re

from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from model_mommy import mommy

def get_data_url(response):
    """
    Returns the url contained in the data-ajax attribute from
    a datatable render.
    """
    matches = re.search("data-ajax=\"(.*?)\"", response.content, re.S | re.M)
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
        return json.loads(response.content)

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
        mommy.make('sample.Employee', _quantity=3)

        # Fetch the ajax
        # Should be have somethin'
        datatable = self.get_datatable(response)
        print datatable
        self.assertEqual(datatable['recordsTotal'], 3)


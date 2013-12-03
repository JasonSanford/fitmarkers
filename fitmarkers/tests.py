from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client, RequestFactory

from fitmarkers.user.tests.factories import UserFactory
from fitmarkers.views import home

class BasePagesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = UserFactory()

    def test_home(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)

    def test_home_redirects_to_dashboard(self):
        request = self.factory.get('/')
        request.user = self.user
        response = home(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('user_dashboard'))

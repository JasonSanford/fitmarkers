import subprocess

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client, RequestFactory

from fitmarkers.user.tests.factories import UserFactory
from fitmarkers.views import home
from fitmarkers.user.views import dashboard

class BasePagesTest(TestCase):
    def setUp(self):
        # TODO: need to start redis to hit a lot of pages
        self.redis_process = subprocess.Popen('redis-server redis-test.conf', shell=True)
        self.client = Client()
        self.factory = RequestFactory()
        self.jason = UserFactory(id=1, first_name='Jason', last_name='Sanford', is_superuser=True)
        self.ellen = UserFactory(id=2, first_name='Ellen', last_name='Sanford')

    def tearDown(self):
        self.redis_process.kill()

    def test_home(self):
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)

    def test_home_redirects_to_dashboard(self):
        request = self.factory.get('/')
        request.user = self.jason
        response = home(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('user_dashboard'))

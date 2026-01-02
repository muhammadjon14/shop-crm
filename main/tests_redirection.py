from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class RedirectionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(username='admin', password='password123', email='admin@test.com')
        self.employee = User.objects.create_user(username='employee', password='password123')

    def test_superuser_redirection(self):
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/admin/')

    def test_employee_redirection(self):
        self.client.login(username='employee', password='password123')
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('pos'))

    def test_unauthenticated_user_no_redirection(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_pos_requires_login(self):
        response = self.client.get(reverse('pos'))
        self.assertRedirects(response, f'/admin/login/?next={reverse("pos")}')

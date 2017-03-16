from django.contrib.auth.models import User
from django.test import TestCase, Client


class LoginTestCase(TestCase):

    def setUp(self):
        User.objects.create_user(
            username='user',
            password='password'
        )

    def test_login_form(self):
        c = Client()
        response = c.get('/login/')
        self.assertTemplateUsed(
            response,
            template_name='login/login.html'
        )

    def test_login_with_correct_password(self):
        c = Client()
        response = c.post('/login/', {
            'username': 'user',
            'password': 'password',
        })
        self.assertRedirects(response, '/')

    def test_login_case_insensitive(self):
        c = Client()
        response = c.post('/login/', {
            'username': 'User',
            'password': 'password',
        })
        self.assertContains(
            response,
            'Please enter a correct username and password.'
        )

    def test_login_invalid_password(self):
        c = Client()
        response = c.post('/login/', {
            'username': 'user',
            'password': 'p4ssword',
        })
        self.assertContains(
            response,
            'Please enter a correct username and password.'
        )

    def test_login_non_existing_user(self):
        c = Client()
        response = c.post('/login/', {
            'username': 'max',
            'password': 'moritz',
        })
        self.assertContains(
            response,
            'Please enter a correct username and password.'
        )


class AdminLoginTestCase(TestCase):

    def setUp(self):
        User.objects.create_user(
            username='user',
            password='password'
        )
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='pass'
        )

    def test_admin_loggedin(self):
        c = Client()
        c.login(username='admin', password='pass')
        response = c.get('/')
        self.assertContains(
            response,
            'Administration'
        )

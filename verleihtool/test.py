from django.contrib.auth.models import User, Group
from django.test import TestCase, Client


class ClientTestCase(TestCase):
    """
    Base test case with convenience methods to login and assert responses

    :author: Benedikt Seidl
    """

    def setUp(self):
        # Create normal user
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='password',
            first_name='Ursula',
            last_name='User'
        )

        # Create superuser
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='pass',
            first_name='Armin',
            last_name='Admin'
        )

        # Create a group
        self.group = Group.objects.create()
        self.user.groups.add(self.group)

    @property
    def as_guest(self):
        return Client()

    @property
    def as_user(self):
        c = Client()
        c.login(username='user', password='password')
        return c

    @property
    def as_superuser(self):
        c = Client()
        c.login(username='admin', password='pass')
        return c

    def assertSuccess(self, response, template):
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template)

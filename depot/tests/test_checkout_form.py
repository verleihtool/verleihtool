from django.contrib.auth.models import User
from depot.models import Depot, Organization
from verleihtool.test import ClientTestCase


class AutoFillTestCase(ClientTestCase):
    """
    Test cases asserting the auto-fill functionality for checkout-form

    :author: Stefan Su
    """
    def setUp(self):
        super(AutoFillTestCase, self).setUp()

        self.user.first_name = 'Ulrich'
        self.user.last_name = 'User'
        self.user.save()

        self.superuser.first_name = 'Armin'
        self.superuser.last_name = 'Admin'
        self.superuser.save()

        organization = Organization.objects.create()

        self.depot = Depot.objects.create(
            name='My Depot',
            organization=organization
        )

    def test_user_logged_in_autofill(self):
        response = self.as_user.get('/depots/%d/' % self.depot.id)

        self.assertInHTML(
            '<input type="text" class="form-control" '
            'name="lastname" value="User" required>',
            response.content.decode()
        )

        self.assertInHTML(
            '<input type="text" class="form-control" '
            'name="firstname" value="Ulrich" required>',
            response.content.decode()
        )

        self.assertInHTML(
            '<input type="email" class="form-control" id="email"'
            'name="email" value="user@example.com" required>',
            response.content.decode()
        )

    def test_not_logged_in_no_autofill(self):
        response = self.as_guest.get('/depots/%d/' % self.depot.id)

        self.assertInHTML(
            '<input type="text" class="form-control" '
            'name="lastname" value="" required>',
            response.content.decode()
        )

        self.assertInHTML(
            '<input type="text" class="form-control" '
            'name="firstname" value="" required>',
            response.content.decode()
        )

        self.assertInHTML(
            '<input type="email" class="form-control" id="email"'
            'name="email" value="" required>',
            response.content.decode()
        )

from depot.models import Depot, Organization
from verleihtool.test import ClientTestCase


class CheckoutFormTestCase(ClientTestCase):
    """
    Test the checkout form by asserting the auto-fill
    functionality for checkout-form

    :author: Stefan Su
    """

    def setUp(self):
        super().setUp()

        organization = Organization.objects.create()

        self.depot = Depot.objects.create(
            name='My Depot',
            organization=organization
        )

    def test_user_logged_in_autofill(self):
        response = self.as_user.get('/depots/%d/rentals/create/' % self.depot.id)

        self.assertInHTML(
            '<input type="text" class="form-control" id="lastname" '
            'name="lastname" value="User" required>',
            response.content.decode()
        )

        self.assertInHTML(
            '<input type="text" class="form-control" id="firstname" '
            'name="firstname" value="Ursula" required>',
            response.content.decode()
        )

        self.assertInHTML(
            '<input type="email" class="form-control" id="email"'
            'name="email" value="user@example.com" required>',
            response.content.decode()
        )

    def test_not_logged_in_no_autofill(self):
        response = self.as_guest.get('/depots/%d/rentals/create/' % self.depot.id)

        self.assertInHTML(
            '<input type="text" class="form-control" id="lastname" '
            'name="lastname" value="" required>',
            response.content.decode()
        )

        self.assertInHTML(
            '<input type="text" class="form-control" id="firstname" '
            'name="firstname" value="" required>',
            response.content.decode()
        )

        self.assertInHTML(
            '<input type="email" class="form-control" id="email"'
            'name="email" value="" required>',
            response.content.decode()
        )

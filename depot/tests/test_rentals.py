from depot.models import Depot, Organization
from rental.models import Rental
from verleihtool.test import ClientTestCase
from datetime import datetime


class RentalsTestCase(ClientTestCase):

    def create_rental(self, depot, firstname, lastname, state):
        return Rental.objects.create(
            depot=depot,
            firstname=firstname,
            lastname=lastname,
            start_date=datetime(2017, 3, 25, 0, 0),
            return_date=datetime(2017, 3, 27, 0, 0),
            state=state
        )

    def setUp(self):
        super().setUp()

        organization = Organization.objects.create(
            name='My organization'
        )

        self.depot1 = Depot.objects.create(
            name='My 1st depot',
            organization=organization
        )

        self.depot2 = Depot.objects.create(
            name='My 2nd depot',
            organization=organization
        )

    def test_depot_rentals_as_guest(self):
        response = self.as_guest.get('/depots/%d/rentals/' % self.depot1.id)
        self.assertEqual(response.status_code, 403)

    def test_depot_rentals_as_depot_manager(self):
        self.depot1.manager_users.add(self.user)
        response = self.as_user.get('/depots/%d/rentals/' % self.depot1.id)
        self.assertSuccess(response, 'depot/rentals.html')

    def test_depot_rentals_show_rental_list(self):
        self.create_rental(self.depot1, 'Dick', 'Sendors', Rental.STATE_PENDING),
        self.create_rental(self.depot1, 'Greg', 'Johnson', Rental.STATE_APPROVED),
        self.create_rental(self.depot2, 'Doris', 'Brier', Rental.STATE_REVOKED)
        self.depot1.manager_users.add(self.user)
        response = self.as_user.get('/depots/%d/rentals/' % self.depot1.id)
        self.assertSuccess(response, 'depot/rentals.html')
        self.assertContains(response, 'Dick Sendors')
        self.assertContains(response, 'Greg Johnson')
        self.assertNotContains(response, 'Doris Brier')
        self.assertContains(response, 'March 25, 2017')
        self.assertContains(response, 'March 27, 2017')
        self.assertContains(response, 'pending')
        self.assertContains(response, 'approved')
        self.assertNotContains(response, 'revoked')
        self.assertNotContains(response, 'declined')
        self.assertNotContains(response, 'returned')

from datetime import datetime
from verleihtool.test import ClientTestCase
from depot.models import Depot, Item, Organization
from rental.models import Rental


class RentalDetailTestCase(ClientTestCase):

    def setUp(self):
        super().setUp()

        organization = Organization.objects.create(
            name='My organization'
        )

        depot = Depot.objects.create(
            name='My depot',
            organization=organization
        )

        self.rental = Rental.objects.create(
            depot=depot,
            start_date=datetime(2017, 3, 25),
            return_date=datetime(2017, 3, 27)
        )

    def test_rental_detail(self):
        response = self.as_guest.get('/rentals/%s/' % self.rental.uuid)
        self.assertSuccess(response, 'rental/detail.html')
        self.assertContains(response, 'March 25, 2017')
        self.assertContains(response, 'March 27, 2017')

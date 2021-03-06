from datetime import datetime
from verleihtool.test import ClientTestCase
from depot.models import Depot, Organization
from rental.models import Rental


class RentalDetailTestCase(ClientTestCase):

    def create_rental(self, state):
        return Rental.objects.create(
            depot=self.depot,
            start_date=datetime(2017, 3, 25),
            return_date=datetime(2017, 3, 27),
            state=state
        )

    def assertButtonCount(self, response, action, count):
        data = {
            'Pending': ('warning', 'Reset'),
            'Revoked': ('danger', 'Revoke'),
            'Approved': ('success', 'Approve'),
            'Declined': ('danger', 'Decline'),
            'Returned': ('info', 'Finish'),
        }[action]

        button = ('<button type="submit" class="btn btn-%s pull-left">%s</button>'
                  % data)

        self.assertInHTML(button, response.content.decode(), count)

    def assertButton(self, response, action):
        self.assertButtonCount(response, action, count=1)

    def assertNotButton(self, response, action):
        self.assertButtonCount(response, action, count=0)

    def setUp(self):
        super().setUp()

        organization = Organization.objects.create(
            name='My organization'
        )

        self.depot = Depot.objects.create(
            name='My depot',
            organization=organization
        )

    def test_rental_detail(self):
        rental = self.create_rental(Rental.STATE_PENDING)
        response = self.as_guest.get('/rentals/%s/' % rental.uuid)
        self.assertSuccess(response, 'rental/detail.html')
        self.assertContains(response, 'March 25, 2017')
        self.assertContains(response, 'March 27, 2017')

    def test_rental_not_found_as_guest(self):
        response = self.as_guest.get('/rentals/I-am-not-a-uuid/')
        self.assertEqual(response.status_code, 404)

    def test_rental_not_found_as_superuser(self):
        response = self.as_superuser.get('/rentals/I-am-not-a-uuid/')
        self.assertEqual(response.status_code, 404)

    def test_buttons_as_guest_pending(self):
        rental = self.create_rental(Rental.STATE_PENDING)
        response = self.as_guest.get('/rentals/%s/' % rental.uuid)
        self.assertButton(response, 'Revoked')
        self.assertNotButton(response, 'Pending')
        self.assertNotButton(response, 'Approved')
        self.assertNotButton(response, 'Declined')
        self.assertNotButton(response, 'Returned')

    def test_buttons_as_guest_revoked(self):
        rental = self.create_rental(Rental.STATE_REVOKED)
        response = self.as_guest.get('/rentals/%s/' % rental.uuid)
        self.assertNotButton(response, 'Revoked')
        self.assertButton(response, 'Pending')
        self.assertNotButton(response, 'Approved')
        self.assertNotButton(response, 'Declined')
        self.assertNotButton(response, 'Returned')

    def test_buttons_as_guest_approved(self):
        rental = self.create_rental(Rental.STATE_APPROVED)
        response = self.as_guest.get('/rentals/%s/' % rental.uuid)
        self.assertButton(response, 'Revoked')
        self.assertNotButton(response, 'Pending')
        self.assertNotButton(response, 'Approved')
        self.assertNotButton(response, 'Declined')
        self.assertNotButton(response, 'Returned')

    def test_buttons_as_guest_declined(self):
        rental = self.create_rental(Rental.STATE_DECLINED)
        response = self.as_guest.get('/rentals/%s/' % rental.uuid)
        self.assertNotButton(response, 'Revoked')
        self.assertNotButton(response, 'Pending')
        self.assertNotButton(response, 'Approved')
        self.assertNotButton(response, 'Declined')
        self.assertNotButton(response, 'Returned')

    def test_buttons_as_guest_returned(self):
        rental = self.create_rental(Rental.STATE_RETURNED)
        response = self.as_guest.get('/rentals/%s/' % rental.uuid)
        self.assertNotButton(response, 'Revoked')
        self.assertNotButton(response, 'Pending')
        self.assertNotButton(response, 'Approved')
        self.assertNotButton(response, 'Declined')
        self.assertNotButton(response, 'Returned')

    def test_buttons_as_depot_manager_pending(self):
        self.depot.manager_users.add(self.user)
        rental = self.create_rental(Rental.STATE_PENDING)
        response = self.as_user.get('/rentals/%s/' % rental.uuid)
        self.assertNotButton(response, 'Revoked')
        self.assertNotButton(response, 'Pending')
        self.assertButton(response, 'Approved')
        self.assertButton(response, 'Declined')
        self.assertNotButton(response, 'Returned')

    def test_buttons_as_depot_manager_revoked(self):
        self.depot.manager_users.add(self.user)
        rental = self.create_rental(Rental.STATE_REVOKED)
        response = self.as_user.get('/rentals/%s/' % rental.uuid)
        self.assertNotButton(response, 'Revoked')
        self.assertButton(response, 'Pending')
        self.assertNotButton(response, 'Approved')
        self.assertNotButton(response, 'Declined')
        self.assertNotButton(response, 'Returned')

    def test_buttons_as_depot_manager_approved(self):
        self.depot.manager_users.add(self.user)
        rental = self.create_rental(Rental.STATE_APPROVED)
        response = self.as_user.get('/rentals/%s/' % rental.uuid)
        self.assertNotButton(response, 'Revoked')
        self.assertButton(response, 'Pending')
        self.assertNotButton(response, 'Approved')
        self.assertButton(response, 'Declined')
        self.assertButton(response, 'Returned')

    def test_buttons_as_depot_manager_declined(self):
        self.depot.manager_users.add(self.user)
        rental = self.create_rental(Rental.STATE_DECLINED)
        response = self.as_user.get('/rentals/%s/' % rental.uuid)
        self.assertNotButton(response, 'Revoked')
        self.assertButton(response, 'Pending')
        self.assertButton(response, 'Approved')
        self.assertNotButton(response, 'Declined')
        self.assertNotButton(response, 'Returned')

    def test_buttons_as_depot_manager_returned(self):
        self.depot.manager_users.add(self.user)
        rental = self.create_rental(Rental.STATE_RETURNED)
        response = self.as_user.get('/rentals/%s/' % rental.uuid)
        self.assertNotButton(response, 'Revoked')
        self.assertNotButton(response, 'Pending')
        self.assertButton(response, 'Approved')
        self.assertNotButton(response, 'Declined')
        self.assertNotButton(response, 'Returned')

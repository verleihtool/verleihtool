from django.contrib.auth.models import User
from depot.models import Depot, Organization
from rental.models import Rental
from verleihtool.test import ClientTestCase
from datetime import datetime


class RentalStateTestCase(ClientTestCase):

    def create_rental(self, state):
        return Rental.objects.create(
            depot=self.depot,
            start_date=datetime(2017, 3, 25),
            return_date=datetime(2017, 3, 27),
            state=state
        )

    def setUp(self):
        super().setUp()

        organization = Organization.objects.create(
            name='My organization'
        )

        self.depot = Depot.objects.create(
            name='My depot',
            organization=organization
        )

    def test_get_not_allowed(self):
        rental = self.create_rental(Rental.STATE_PENDING)
        response = self.as_guest.get('/rentals/%s/state/' % rental.uuid)
        self.assertEqual(response.status_code, 405)

    def test_rental_not_found_as_guest(self):
        response = self.as_guest.post('/rentals/I-am-not-a-uuid/state/')
        self.assertEqual(response.status_code, 404)

    def test_rental_not_found_as_superuser(self):
        response = self.as_superuser.post('/rentals/I-am-not-a-uuid/state/')
        self.assertEqual(response.status_code, 404)

    def test_update_rental_state_as_depot_manager(self):
        data = [
            (Rental.STATE_PENDING, Rental.STATE_REVOKED),
            (Rental.STATE_APPROVED, Rental.STATE_REVOKED),
            (Rental.STATE_REVOKED, Rental.STATE_PENDING),
            (Rental.STATE_APPROVED, Rental.STATE_PENDING),
            (Rental.STATE_DECLINED, Rental.STATE_PENDING),
            (Rental.STATE_PENDING, Rental.STATE_APPROVED),
            (Rental.STATE_DECLINED, Rental.STATE_APPROVED),
            (Rental.STATE_RETURNED, Rental.STATE_APPROVED),
            (Rental.STATE_PENDING, Rental.STATE_DECLINED),
            (Rental.STATE_APPROVED, Rental.STATE_DECLINED),
            (Rental.STATE_APPROVED, Rental.STATE_RETURNED)
        ]

        self.depot.manager_users.add(self.user)

        for initial_state, expected_state in data:
            rental = self.create_rental(initial_state)
            response = self.as_user.post('/rentals/%s/state/' % rental.uuid, {
                'state': expected_state
            })
            self.assertRedirects(response, '/rentals/%s/' % rental.uuid)
            rental.refresh_from_db()
            self.assertEqual(rental.state, expected_state)

    def test_invalid_rental_state_as_depot_manager(self):
        data = [
            (Rental.STATE_REVOKED, Rental.STATE_REVOKED),
            (Rental.STATE_DECLINED, Rental.STATE_REVOKED),
            (Rental.STATE_RETURNED, Rental.STATE_REVOKED),
            (Rental.STATE_PENDING, Rental.STATE_PENDING),
            (Rental.STATE_RETURNED, Rental.STATE_PENDING),
            (Rental.STATE_REVOKED, Rental.STATE_APPROVED),
            (Rental.STATE_APPROVED, Rental.STATE_APPROVED),
            (Rental.STATE_REVOKED, Rental.STATE_DECLINED),
            (Rental.STATE_DECLINED, Rental.STATE_DECLINED),
            (Rental.STATE_RETURNED, Rental.STATE_DECLINED),
            (Rental.STATE_PENDING, Rental.STATE_RETURNED),
            (Rental.STATE_REVOKED, Rental.STATE_RETURNED),
            (Rental.STATE_DECLINED, Rental.STATE_RETURNED),
            (Rental.STATE_RETURNED, Rental.STATE_RETURNED),
            (Rental.STATE_PENDING, '')
        ]

        self.depot.manager_users.add(self.user)

        for initial_state, action in data:
            rental = self.create_rental(initial_state)
            response = self.as_user.post('/rentals/%s/state/' % rental.uuid, {
                'state': action
            })
            self.assertEqual(response.status_code, 403)

    def test_update_rental_state_as_guest(self):
        data = [
            (Rental.STATE_PENDING, Rental.STATE_REVOKED, Rental.STATE_REVOKED),
            (Rental.STATE_APPROVED, Rental.STATE_REVOKED, Rental.STATE_REVOKED),
            (Rental.STATE_REVOKED, Rental.STATE_PENDING, Rental.STATE_PENDING)
        ]

        for initial_state, action, expected_state in data:
            rental = self.create_rental(initial_state)
            response = self.as_guest.post('/rentals/%s/state/' % rental.uuid, {
                'state': action
            })
            self.assertRedirects(response, '/rentals/%s/' % rental.uuid)
            rental.refresh_from_db()
            self.assertEqual(rental.state, expected_state)

    def test_invalid_rental_state_as_guest(self):
        data = [
            (Rental.STATE_REVOKED, Rental.STATE_REVOKED),
            (Rental.STATE_DECLINED, Rental.STATE_REVOKED),
            (Rental.STATE_RETURNED, Rental.STATE_REVOKED),
            (Rental.STATE_PENDING, Rental.STATE_PENDING),
            (Rental.STATE_APPROVED, Rental.STATE_PENDING),
            (Rental.STATE_DECLINED, Rental.STATE_PENDING),
            (Rental.STATE_RETURNED, Rental.STATE_PENDING),
            (Rental.STATE_PENDING, Rental.STATE_APPROVED),
            (Rental.STATE_REVOKED, Rental.STATE_APPROVED),
            (Rental.STATE_APPROVED, Rental.STATE_APPROVED),
            (Rental.STATE_DECLINED, Rental.STATE_APPROVED),
            (Rental.STATE_RETURNED, Rental.STATE_APPROVED),
            (Rental.STATE_PENDING, Rental.STATE_DECLINED),
            (Rental.STATE_REVOKED, Rental.STATE_DECLINED),
            (Rental.STATE_APPROVED, Rental.STATE_DECLINED),
            (Rental.STATE_DECLINED, Rental.STATE_DECLINED),
            (Rental.STATE_RETURNED, Rental.STATE_DECLINED),
            (Rental.STATE_PENDING, Rental.STATE_RETURNED),
            (Rental.STATE_REVOKED, Rental.STATE_RETURNED),
            (Rental.STATE_APPROVED, Rental.STATE_RETURNED),
            (Rental.STATE_DECLINED, Rental.STATE_RETURNED),
            (Rental.STATE_RETURNED, Rental.STATE_RETURNED),
            (Rental.STATE_PENDING, '')
        ]

        for initial_state, action in data:
            rental = self.create_rental(initial_state)
            response = self.as_guest.post('/rentals/%s/state/' % rental.uuid, {
                'state': action
            })
            self.assertEqual(response.status_code, 403)

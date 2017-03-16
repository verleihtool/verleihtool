from verleihtool.test import TestCase
from depot.models import Depot


def create_depot(name, active=True):
    return Depot.objects.create(name=name, active=active)


class DepotIndexTestCase(TestCase):

    def test_depot_index_as_guest_no_depots(self):
        response = self.as_guest.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertQuerysetEqual(response.context['depot_list'], [])
        self.assertContains(response, 'No depots available :(')

    def test_depot_index_as_guest_active_depot(self):
        depot = create_depot('active depot')
        response = self.as_guest.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertQuerysetEqual(
            response.context['depot_list'], ['<Depot: Depot active depot>']
        )
        self.assertContains(response, depot.name)

    def test_depot_index_as_guest_archived_depot(self):
        depot = create_depot('archived depot', active=False)
        response = self.as_guest.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertQuerysetEqual(response.context['depot_list'], [])
        self.assertContains(response, 'No depots available')
        self.assertNotContains(response, depot.name)

    def test_depot_index_as_guest_active_and_archived_depot(self):
        active_depot = create_depot('active depot')
        archived_depot = create_depot('archived depot', active=False)
        response = self.as_guest.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertQuerysetEqual(
            response.context['depot_list'], ['<Depot: Depot active depot>']
        )
        self.assertContains(response, active_depot.name)
        self.assertNotContains(response, archived_depot.name)

    def test_depot_index_as_user_active_and_archived_depot(self):
        active_depot = create_depot('active depot')
        archived_depot = create_depot('archived depot', active=False)
        response = self.as_user.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertQuerysetEqual(
            response.context['depot_list'], ['<Depot: Depot active depot>']
        )
        self.assertContains(response, active_depot.name)
        self.assertNotContains(response, archived_depot.name)

    def test_depot_index_as_superuser_active_and_archived_depot(self):
        active_depot = create_depot('active depot')
        archived_depot = create_depot('archived depot', active=False)
        response = self.as_superuser.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertQuerysetEqual(
            response.context['depot_list'].order_by('id'),
            ['<Depot: Depot active depot>', '<Depot: Depot archived depot>']
        )
        self.assertContains(response, active_depot.name)
        self.assertContains(response, archived_depot.name)

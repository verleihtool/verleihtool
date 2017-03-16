from django.test import TestCase, Client
from depot.models import Depot


def create_depot(name, state):
    return Depot.objects.create(name=name, active=state)


class DepotIndexTestCase(TestCase):

    def test_depot_index_template(self):
        response = self.client.get('/depots/')
        self.assertTemplateUsed(
            response,
            template_name='depot/index.html'
        )

    def test_depot_index_with_no_depots(self):
        response = self.client.get('/depots/')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['depot_list'], [])
        self.assertContains(response, 'No depots available :(')

    def test_depot_index_with_active_depot(self):
        depot = create_depot('active depot', True)
        response = self.client.get('/depots/')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['depot_list'], ['<Depot: Depot active depot>']
        )
        self.assertContains(response, depot.name)

    def test_depot_index_with_archived_depot(self):
        depot = create_depot('archived depot', False)
        response = self.client.get('/depots/')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['depot_list'], [])
        self.assertContains(response, 'No depots available')
        self.assertNotContains(response, depot.name)

    def test_depot_index_with_active_and_archived_depot(self):
        active_depot = create_depot('active depot', True)
        archived_depot = create_depot('archived depot', False)
        response = self.client.get('/depots/')
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['depot_list'], ['<Depot: Depot active depot>']
        )
        self.assertContains(response, active_depot.name)
        self.assertNotContains(response, archived_depot.name)

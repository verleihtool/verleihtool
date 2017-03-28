from depot.models import Depot, Item, Organization
from verleihtool.test import ClientTestCase


class DepotDetailTestCase(ClientTestCase):

    def create_item(self, name, visibility):
        Item.objects.create(
            name=name,
            depot=self.depot,
            quantity=1,
            visibility=visibility
        )

    def setUp(self):
        super().setUp()

        self.organization = Organization.objects.create()

        self.depot = Depot.objects.create(
            name='My Depot',
            organization=self.organization
        )

        self.inactive_depot = Depot.objects.create(
            name='My Inactive Depot',
            organization=self.organization,
            active=False
        )

    def test_show_depot_name(self):
        response = self.as_guest.get('/depots/%d/' % self.depot.id)
        self.assertSuccess(response, 'depot/detail.html')
        self.assertContains(response, 'My Depot')

    def test_inactive_depot_forbidden(self):
        response = self.as_guest.get('/depots/%d/' % self.inactive_depot.id)
        self.assertEqual(response.status_code, 403)

    def test_inactive_depot_found_when_organization_manager(self):
        self.organization.managers.add(self.user)
        response = self.as_superuser.get('/depots/%d/' % self.inactive_depot.id)
        self.assertSuccess(response, 'depot/detail.html')
        self.assertContains(response, 'My Inactive Depot')

    def test_inactive_depot_found_when_superuser(self):
        response = self.as_superuser.get('/depots/%d/' % self.inactive_depot.id)
        self.assertSuccess(response, 'depot/detail.html')
        self.assertContains(response, 'My Inactive Depot')

    def test_no_manage_link_for_guest(self):
        response = self.as_guest.get('/depots/%d/' % self.depot.id)
        self.assertSuccess(response, 'depot/detail.html')
        self.assertNotContains(response, '/admin/depot/depot/%d/change/' % self.depot.id)

    def test_no_manage_link_for_normal_user(self):
        response = self.as_user.get('/depots/%d/' % self.depot.id)
        self.assertSuccess(response, 'depot/detail.html')
        self.assertNotContains(response, '/admin/depot/depot/%d/change/' % self.depot.id)

    def test_manage_link_for_depot_manager(self):
        self.depot.manager_users.add(self.user)
        response = self.as_user.get('/depots/%d/' % self.depot.id)
        self.assertSuccess(response, 'depot/detail.html')
        self.assertContains(response, '/admin/depot/depot/%d/change/' % self.depot.id)

    def test_manage_link_for_superuser(self):
        response = self.as_superuser.get('/depots/%d/' % self.depot.id)
        self.assertSuccess(response, 'depot/detail.html')
        self.assertContains(response, '/admin/depot/depot/%d/change/' % self.depot.id)

    def test_public_items_for_guest(self):
        self.create_item('Public Item', Item.VISIBILITY_PUBLIC)
        self.create_item('Private Item', Item.VISIBILITY_PRIVATE)
        response = self.as_guest.get('/depots/%d/' % self.depot.id)
        self.assertSuccess(response, 'depot/detail.html')
        self.assertContains(response, 'Public Item')
        self.assertNotContains(response, 'Private Item')

    def test_public_items_for_normal_user(self):
        self.create_item('Public Item', Item.VISIBILITY_PUBLIC)
        self.create_item('Private Item', Item.VISIBILITY_PRIVATE)
        response = self.as_user.get('/depots/%d/' % self.depot.id)
        self.assertSuccess(response, 'depot/detail.html')
        self.assertContains(response, 'Public Item')
        self.assertNotContains(response, 'Private Item')

    def test_all_items_as_organization_member(self):
        self.create_item('Public Item', Item.VISIBILITY_PUBLIC)
        self.create_item('Private Item', Item.VISIBILITY_PRIVATE)
        self.organization.groups.add(self.group)
        response = self.as_user.get('/depots/%d/' % self.depot.id)
        self.assertSuccess(response, 'depot/detail.html')
        self.assertContains(response, 'Public Item')
        self.assertContains(response, 'Private Item')

    def test_all_items_as_superuser(self):
        self.create_item('Public Item', Item.VISIBILITY_PUBLIC)
        self.create_item('Private Item', Item.VISIBILITY_PRIVATE)
        response = self.as_superuser.get('/depots/%d/' % self.depot.id)
        self.assertSuccess(response, 'depot/detail.html')
        self.assertContains(response, 'Public Item')
        self.assertContains(response, 'Private Item')

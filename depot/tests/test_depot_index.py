from verleihtool.test import ClientTestCase
from depot.models import Depot, Item, Organization


def create_organization(name):
    return Organization.objects.create(name=name)


def create_depot(name, active=True, organization=None):
    if organization is None:
        organization = create_organization('My organization')

    depot = Depot.objects.create(
        name=name, active=active, organization=organization
    )

    for i in range(42):
        Item.objects.create(
            name='Item %d' % i,
            depot=depot,
            quantity=1,
            visibility=Item.VISIBILITY_PUBLIC
        )

    Item.objects.create(
        depot=depot, quantity=1, visibility=Item.VISIBILITY_INTERNAL
    )

    return depot


class DepotIndexTestCase(ClientTestCase):
    """
    Test the index page for all depots at `/depots/`

    :author: Leo Tappe
    :author: Benedikt Seidl
    """

    def test_as_guest_no_depots(self):
        response = self.as_guest.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertContains(response, 'No depots available')

    def test_as_user_no_depots(self):
        response = self.as_user.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertContains(response, 'No depots available')

    def test_as_guest_active_depot(self):
        create_depot('My active depot')
        response = self.as_guest.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertContains(response, 'My active depot')
        # There are 42 items in the depot
        self.assertContains(response, '42')

    def test_as_guest_archived_depot(self):
        create_depot('My archived depot', active=False)
        response = self.as_guest.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertContains(response, 'No depots available')
        self.assertNotContains(response, 'My archived depot')

    def test_as_guest_active_and_archived_depot(self):
        create_depot('My active depot')
        create_depot('My archived depot', active=False)
        response = self.as_guest.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertContains(response, 'My active depot')
        self.assertNotContains(response, 'My archived depot')

    def test_as_user_active_and_archived_depot(self):
        create_depot('My active depot')
        create_depot('My archived depot', active=False)
        response = self.as_user.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertContains(response, 'My active depot')
        self.assertNotContains(response, 'My archived depot')

    def test_as_superuser_active_and_archived_depot(self):
        create_depot('My active depot')
        create_depot('My archived depot', active=False)
        response = self.as_superuser.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertContains(response, 'My active depot')
        self.assertNotContains(response, 'My archived depot')

    def test_as_guest_organizations_with_active_depots(self):
        organization = create_organization('My empty organization')
        create_depot('My active depot')
        create_depot('My archived depot', active=False, organization=organization)

        response = self.as_guest.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertContains(response, 'My organization')
        self.assertNotContains(response, 'My empty organization')

    def test_as_user_organizations_with_active_depots(self):
        organization = create_organization('My empty organization')
        create_depot('My active depot')
        create_depot('My archived depot', active=False, organization=organization)

        response = self.as_user.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertContains(response, 'My organization')
        self.assertNotContains(response, 'My empty organization')

    def test_as_omg_organization_with_archived_depot(self):
        organization = create_organization('My managed organization')
        create_depot('My archived depot', active=False, organization=organization)
        organization.managers.add(self.user)

        response = self.as_user.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertNotContains(response, 'My archived depot')

    def test_as_superuser_organization_with_archived_depot(self):
        organization = create_organization('My managed organization')
        create_depot('My archived depot', active=False, organization=organization)
        organization.managers.add(self.user)

        response = self.as_user.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertNotContains(response, 'My archived depot')

    def test_as_guest_no_manage_link(self):
        depot = create_depot('My active depot')
        response = self.as_guest.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertNotContains(
            response, '/admin/depot/organization/%d/change/' % depot.organization_id
        )

    def test_as_user_no_manage_link(self):
        depot = create_depot('My active depot')
        response = self.as_user.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertNotContains(
            response, '/admin/depot/organization/%d/change/' % depot.organization_id
        )

    def test_as_omg_manage_link(self):
        depot = create_depot('My active depot')
        depot.organization.managers.add(self.user)
        response = self.as_user.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertContains(
            response, '/admin/depot/organization/%d/change/' % depot.organization_id
        )

    def test_as_superuser_manage_link(self):
        depot = create_depot('My active depot')
        response = self.as_superuser.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertContains(
            response, '/admin/depot/organization/%d/change/' % depot.organization_id
        )

    def test_managers_list(self):
        organization = create_organization('My organization')
        create_depot('My depot', organization=organization)
        organization.managers.add(self.user)
        response = self.as_guest.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertContains(response, 'This organization is managed by Ursula User.')

    def test_no_managers(self):
        organization = create_organization('My organization')
        create_depot('My depot', organization=organization)
        response = self.as_guest.get('/depots/')
        self.assertSuccess(response, 'depot/index.html')
        self.assertContains(response, 'This organization is managed by no one apparently.')

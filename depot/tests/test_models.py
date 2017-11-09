from django.test import TestCase
from depot.models import Depot, Item, Organization


class OrganizationTestCase(TestCase):

    def test_str(self):
        organization = Organization(name='My organization')
        self.assertEqual(organization.__str__(), 'My organization')


class DepotTestCase(TestCase):

    def test_str(self):
        depot = Depot(name='My depot')
        self.assertEqual(depot.__str__(), 'My depot')


class ItemTestCase(TestCase):

    def test_str(self):
        item = Item(name='My item')
        self.assertEqual(item.__str__(), 'My item')

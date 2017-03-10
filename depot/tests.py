from django.test import TestCase
from .models import Depot, Item

class DepotTestCase(TestCase):

    def test_str(self):
        depot = Depot(1, "My depot")
        self.assertEqual(depot.__str__(), "Depot My depot")

class ItemTestCase(TestCase):

    def test_str(self):
        depot = Depot(2, "My depot")
        item = Item(1, "My item", 5, 2, depot, "My shelf")
        self.assertEqual(item.__str__(), "5 unit(s) of My item (visib.: 2) in My shelf")

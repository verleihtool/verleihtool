from django.test import TestCase
from .models import Depot

class DepotTestCase(TestCase):

    def test_str(self):
        depot = Depot(1, "My depot")
        self.assertEqual(depot.__str__(), "Depot My depot")

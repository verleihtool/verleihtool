from django.test import TestCase
from .models import Rental


class RentalTestCase(TestCase):

    def test_str(self):
        rental = Rental(name='Fitnessflow')
        self.assertEqual(rental.__str__(), 'Rental by Fitnessflow')

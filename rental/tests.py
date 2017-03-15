import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Rental


class RentalTestCase(TestCase):

    def test_clean__valid_rental(self):
        rental = Rental(
            start_date=datetime.datetime(2017, 3, 15),
            return_date=datetime.datetime(2017, 3, 17)
        )
        rental.clean()

    def test_clean__same_dates(self):
        rental = Rental(
            start_date=datetime.datetime(2017, 3, 15),
            return_date=datetime.datetime(2017, 3, 15)
        )
        rental.clean()

    def test_clean__invalid_rental(self):
        rental = Rental(
            start_date=datetime.datetime(2017, 3, 15),
            return_date=datetime.datetime(2017, 3, 13)
        )
        with self.assertRaises(ValidationError):
            rental.clean()

    def test_str(self):
        rental = Rental(name='Fitnessflow')
        self.assertEqual(rental.__str__(), 'Rental by Fitnessflow')

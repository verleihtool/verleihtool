import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Rental, ItemRental
from depot.models import Depot, Item


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


class ItemRentalTestCase(TestCase):

    def test_clean__valid_data(self):
        itemRental = ItemRental(
            rental=Rental(depot_id=123),
            item=Item(quantity=42, depot_id=123),
            quantity=12
        )
        itemRental.clean()

    def test_clean__negative_amount(self):
        itemRental = ItemRental(
            rental=Rental(),
            item=Item(quantity=42),
            quantity=-1
        )
        with self.assertRaises(ValidationError):
            itemRental.clean()

    def test_clean__zero_amount(self):
        itemRental = ItemRental(
            rental=Rental(),
            item=Item(quantity=42),
            quantity=0
        )
        with self.assertRaises(ValidationError):
            itemRental.clean()

    def test_clean__greater_amount(self):
        itemRental = ItemRental(
            rental=Rental(),
            item=Item(quantity=42),
            quantity=56
        )
        with self.assertRaises(ValidationError):
            itemRental.clean()

    def test_clean__different_depots(self):
        itemRental = ItemRental(
            rental=Rental(depot_id=123),
            item=Item(quantity=42, depot_id=456),
            quantity=12
        )
        with self.assertRaises(ValidationError):
            itemRental.clean()

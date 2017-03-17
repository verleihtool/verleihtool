import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Rental, ItemRental
from depot.models import Item


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

    def setUp(self):
        self.rental = Rental(
            start_date=datetime.datetime(2017, 3, 17),
            return_date=datetime.datetime(2017, 3, 19)
        )
        self.item = Item(
            name="My Item",
            quantity=42
        )

    def test_clean__valid_data(self):
        itemRental = ItemRental(
            rental=self.rental,
            item=self.item,
            quantity=12
        )
        itemRental.clean()

    def test_clean__negative_amount(self):
        itemRental = ItemRental(
            rental=self.rental,
            item=self.item,
            quantity=-1
        )
        with self.assertRaises(ValidationError):
            itemRental.clean()

    def test_clean__zero_amount(self):
        itemRental = ItemRental(
            rental=self.rental,
            item=self.item,
            quantity=0
        )
        with self.assertRaises(ValidationError):
            itemRental.clean()

    def test_clean__greater_amount(self):
        itemRental = ItemRental(
            rental=self.rental,
            item=self.item,
            quantity=56
        )
        with self.assertRaises(ValidationError):
            itemRental.clean()

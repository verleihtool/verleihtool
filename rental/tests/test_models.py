from datetime import datetime, timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from rental.models import Rental, ItemRental
from depot.models import Depot, Item, Organization
from django.contrib.auth.models import Group, User


class RentalTestCase(TestCase):

    def test_clean__valid_rental(self):
        rental = Rental(
            depot=Depot(),
            start_date=datetime.now() + timedelta(days=1),
            return_date=datetime.now() + timedelta(days=3)
        )
        rental.clean()

    def test_clean__same_dates(self):
        rental = Rental(
            depot=Depot(),
            start_date=datetime.now() + timedelta(days=1),
            return_date=datetime.now() + timedelta(days=1)
        )
        rental.clean()

    def test_clean__return_date_before_start_date(self):
        rental = Rental(
            depot=Depot(),
            start_date=datetime.now() + timedelta(days=3),
            return_date=datetime.now() + timedelta(days=1)
        )
        with self.assertRaises(ValidationError):
            rental.clean()

    def test_clean__archived_depot(self):
        rental = Rental(
            depot=Depot(active=False),
            start_date=datetime.now() + timedelta(days=1),
            return_date=datetime.now() + timedelta(days=3)
        )
        with self.assertRaises(ValidationError):
            rental.clean()

    def test_clean__past_start_date(self):
        rental = Rental(
            depot=Depot(),
            start_date=datetime.now() + timedelta(days=-1),
            return_date=datetime.now() + timedelta(days=3)
        )
        rental.clean()

    def test_str(self):
        rental = Rental(firstname='Fitness', lastname='Flow')
        self.assertEqual(rental.__str__(), 'Rental by Fitness Flow')


class ItemRentalTestCase(TestCase):

    def setUp(self):
        group = Group.objects.create()
        self.organization = Organization.objects.create()
        self.user_member = User.objects.create(username='Bro-A')
        self.user_member.groups.add(group)
        self.organization.groups.add(group)
        self.user_not_member = User.objects.create(username='Bro-B')
        self.depotA = Depot.objects.create(organization=self.organization)
        self.depotB = Depot.objects.create(organization=self.organization)

    def test_clean__valid_data(self):
        itemRental = ItemRental(
            rental=Rental(depot=self.depotA, user=self.user_member),
            item=Item(visibility=Item.VISIBILITY_PUBLIC, quantity=42, depot=self.depotA),
            quantity=12
        )
        itemRental.clean()

    def test_clean__not_public_member(self):
        itemRental = ItemRental(
            rental=Rental(depot=self.depotA, user=self.user_member),
            item=Item(visibility=Item.VISIBILITY_PRIVATE, quantity=42, depot=self.depotA),
            quantity=12
        )
        itemRental.clean()

    def test_clean__not_public_not_member(self):
        itemRental = ItemRental(
            rental=Rental(depot=self.depotA, user=self.user_not_member),
            item=Item(visibility=Item.VISIBILITY_PRIVATE, quantity=42, depot=self.depotA),
            quantity=12
        )
        with self.assertRaises(ValidationError):
            itemRental.clean()

    def test_clean__negative_amount(self):
        itemRental = ItemRental(
            rental=Rental(depot=self.depotA, user=self.user_member),
            item=Item(quantity=42),
            quantity=-1
        )
        with self.assertRaises(ValidationError):
            itemRental.clean()

    def test_clean__zero_amount(self):
        itemRental = ItemRental(
            rental=Rental(depot=self.depotA, user=self.user_member),
            item=Item(quantity=42),
            quantity=0
        )
        with self.assertRaises(ValidationError):
            itemRental.clean()

    def test_clean__greater_amount(self):
        itemRental = ItemRental(
            rental=Rental(depot=self.depotA, user=self.user_member),
            item=Item(quantity=42),
            quantity=56
        )
        with self.assertRaises(ValidationError):
            itemRental.clean()

    def test_clean__different_depots(self):
        itemRental = ItemRental(
            rental=Rental(depot=self.depotA, user=self.user_member),
            item=Item(quantity=42, depot=self.depotB),
            quantity=12
        )
        with self.assertRaises(ValidationError):
            itemRental.clean()

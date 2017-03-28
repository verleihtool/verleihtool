from verleihtool.test import ClientTestCase
from depot.models import Depot, Item, Organization
from rental.models import Rental, ItemRental
from depot.availability import get_availability_intervals
from datetime import datetime, timedelta


class AvailabilityAlgoTestCase(ClientTestCase):

    def setUp(self):
        super().setUp()
        self.organization = Organization.objects.create()
        self.depot = Depot.objects.create(
            name='Availability Depot',
            organization=self.organization,
            active=True
        )
        self.item = Item.objects.create(
            depot=self.depot,
            quantity=10,
            visibility=Item.VISIBILITY_PUBLIC
        )
        self.start = datetime.now() + timedelta(days=3)
        self.end = datetime.now() + timedelta(days=7)

    def create_conflicting_rental(self, start, end, quantity):
        rental = Rental.objects.create(
            depot=self.depot,
            start_date=start,
            return_date=end
        )
        ItemRental.objects.create(
            rental=rental,
            item=self.item,
            quantity=quantity
        )
        return rental

    def create_non_conflicting_rental(self, start, end):
        rental = Rental.objects.create(
            depot=self.depot,
            start_date=start,
            return_date=end
        )
        item = Item.objects.create(
            name='irrelevant item',
            depot=self.depot,
            quantity=10,
            visibility=Item.VISIBILITY_PUBLIC
        )
        ItemRental.objects.create(
            rental=rental,
            item=item,
            quantity=3
        )
        return rental

    def test_no_overlap(self):
        start = self.end + timedelta(days=1)
        end = self.end + timedelta(days=2)
        rental = self.create_conflicting_rental(start, end, 3)
        rentals = [rental]
        intervals = get_availability_intervals(
            self.start, self.end, self.item, rentals)
        expected = [[self.start, self.end, 10]]
        self.assertEqual(intervals, expected)

    def test_not_relevant(self):
        start = self.start + timedelta(days=1)
        end = self.end + timedelta(days=-1)
        rental = self.create_non_conflicting_rental(start, end)
        rentals = [rental]
        intervals = get_availability_intervals(
            self.start, self.end, self.item, rentals)
        expected = [
            [self.start, self.end, 10]
        ]
        self.assertEqual(intervals, expected)

    def test_completely_enclosing(self):
        start = self.start + timedelta(days=-1)
        end = self.end + timedelta(days=1)
        rental = self.create_conflicting_rental(start, end, 3)
        rentals = [rental]
        intervals = get_availability_intervals(
            self.start, self.end, self.item, rentals)
        expected = [[self.start, self.end, 7]]
        self.assertEqual(intervals, expected)

    def test_completely_enclosed(self):
        start = self.start + timedelta(days=1)
        end = self.end + timedelta(days=-1)
        rental = self.create_conflicting_rental(start, end, 3)
        rentals = [rental]
        intervals = get_availability_intervals(
            self.start, self.end, self.item, rentals)
        expected = [
            [self.start, start, 10],
            [start, end, 7],
            [end, self.end, 10]
        ]
        self.assertEqual(intervals, expected)

    def test_left_overlap(self):
        start = self.start + timedelta(days=-1)
        end = self.start + timedelta(days=1)
        rental = self.create_conflicting_rental(start, end, 3)
        rentals = [rental]
        intervals = get_availability_intervals(
            self.start, self.end, self.item, rentals)
        expected = [
            [self.start, end, 7],
            [end, self.end, 10]
        ]
        self.assertEqual(intervals, expected)

    def test_left_and_right_no_triple_overlap(self):
        left_start = self.start + timedelta(days=-1)
        left_end = self.start + timedelta(days=1)
        left_rental = self.create_conflicting_rental(left_start, left_end, 3)
        right_start = self.end + timedelta(days=-1)
        right_end = self.end + timedelta(days=1)
        right_rental = self.create_conflicting_rental(right_start, right_end, 3)
        rentals = [left_rental, right_rental]
        intervals = get_availability_intervals(
            self.start, self.end, self.item, rentals)
        expected = [
            [self.start, left_end, 7],
            [left_end, right_start, 10],
            [right_start, self.end, 7]
        ]
        self.assertEqual(intervals, expected)

    def test_left_and_right_triple_overlap(self):
        left_start = self.start + timedelta(days=-1)
        left_end = self.end + timedelta(days=-1)
        left_rental = self.create_conflicting_rental(left_start, left_end, 3)
        right_start = self.start + timedelta(days=1)
        right_end = self.end + timedelta(days=1)
        right_rental = self.create_conflicting_rental(right_start, right_end, 3)
        rentals = [left_rental, right_rental]
        intervals = get_availability_intervals(
            self.start, self.end, self.item, rentals)
        expected = [
            [self.start, right_start, 7],
            [right_start, left_end, 4],
            [left_end, self.end, 7]
        ]
        self.assertEqual(intervals, expected)

    def test_enclosing_and_enclosed(self):
        enclosed_start = self.start + timedelta(days=1)
        enclosed_end = self.end + timedelta(days=-1)
        enclosed_rental = self.create_conflicting_rental(enclosed_start, enclosed_end, 3)
        enclosing_start = self.start + timedelta(days=-1)
        enclosing_end = self.end + timedelta(days=1)
        enclosing_rental = self.create_conflicting_rental(enclosing_start, enclosing_end, 3)
        rentals = [
            enclosed_rental,
            enclosing_rental,
        ]
        intervals = get_availability_intervals(
            self.start, self.end, self.item, rentals)
        expected = [
            [self.start, enclosed_start, 7],
            [enclosed_start, enclosed_end, 4],
            [enclosed_end, self.end, 7]
        ]
        self.assertEqual(intervals, expected)

    def test_start_exactly_on_end_of_rental(self):
        start = self.start + timedelta(days=-1)
        end = self.start
        rental = self.create_conflicting_rental(start, end, 3)
        rentals = [rental]
        intervals = get_availability_intervals(
            self.start, self.end, self.item, rentals)
        expected = [
            [self.start, self.end, 10]
        ]
        self.assertEqual(intervals, expected)

    def test_exactly_matching_rental_time_frame(self):
        rental = self.create_conflicting_rental(self.start, self.end, 3)
        rentals = [rental]
        intervals = get_availability_intervals(
            self.start, self.end, self.item, rentals)
        expected = [
            [self.start, self.end, 7]
        ]
        self.assertEqual(intervals, expected)

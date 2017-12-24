# from django.core import mail
# from django.test import TestCase
from datetime import timedelta, datetime

from depot.models import Organization, Depot, Item
from django.core import mail

from rental.models import Rental, ItemRental
from verleihtool.test import ClientTestCase
from django.core import management


class ReminderTest(ClientTestCase):
    CONST_EARLY = datetime(2017, 6, 15)
    CONST_LATER = datetime(2017, 6, 20)
    CONST_INTERVAL = timedelta(days=7)

    def setUp(self):
        super().setUp()

        organization = Organization.objects.create(
            name='Maz Kanata'
        )

        self.depot = Depot.objects.create(
            name='Maz\'s Storage Room Downstairs',
            organization=organization,
            active=True
        )

        self.item = Item.objects.create(
            name='Luke\'s light saber',
            depot=self.depot,
            quantity=2,
            visibility=Item.VISIBILITY_PUBLIC
        )

        self.due_for_a_week = Rental.objects.create(
            depot=self.depot,
            firstname='Rey',
            lastname='Nobody',
            email='rey@theforce.com',
            start_date=datetime.today() - self.CONST_INTERVAL - timedelta(days=19),
            return_date=datetime.today() - self.CONST_INTERVAL,
            state='2'
        )

        ItemRental.objects.create(
            rental=self.due_for_a_week,
            item=self.item,
            quantity=1
        )

        self.due_for_two_days = Rental.objects.create(
            depot=self.depot,
            firstname='Finn',
            lastname='Somebody',
            email='finn@firstorder.com',
            start_date=datetime.today() - self.CONST_INTERVAL + timedelta(5),
            return_date=datetime.today() - timedelta(days=2),
            state='2'
        )

        ItemRental.objects.create(
            rental=self.due_for_two_days,
            item=self.item,
            quantity=1
        )

    def testOneWeekReminder(self):
        management.call_command('check_for_maturity', '7')

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(
            mail.outbox[0].subject,
            '[Verleihtool] Rey Nobody\'s rental request from "Maz\'s Storage Room Downstairs" '
            'has been due for 7 days!'
        )
        self.assertEqual(
            mail.outbox[1].subject,
            '[Verleihtool] The rental request from "Maz\'s Storage Room Downstairs" '
            'has been due for 7 days, Rey Nobody!'
        )

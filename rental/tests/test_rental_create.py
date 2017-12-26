import re
from datetime import datetime, timedelta
from depot.models import Depot, Item, Organization
from django.core import mail
from verleihtool.test import ClientTestCase


class RentalCreateTestCase(ClientTestCase):

    def setUp(self):
        super().setUp()

        self.organization = Organization.objects.create()
        self.depot = Depot.objects.create(
            name='My Depot',
            organization=self.organization,
            active=True
        )
        self.item = Item.objects.create(
            name='My Item',
            depot=self.depot,
            quantity=1,
            visibility=Item.VISIBILITY_PUBLIC
        )

    def test_mail_sent(self):
        start_date = datetime.now() + timedelta(days=1)
        return_date = datetime.now() + timedelta(days=3)

        response = self.as_guest.post('/rentals/create/', {
            'firstname': 'Guest',
            'lastname': 'User',
            'depot_id': self.depot.id,
            'email': 'guest@user.com',
            'purpose': 'None',
            'start_date': start_date.strftime('%Y-%m-%d %H:%M'),
            'return_date': return_date.strftime('%Y-%m-%d %H:%M'),
            'item-%d-quantity' % self.item.id: 1
        })

        m = re.fullmatch(r'/rentals/([^/]*)/', response.url)
        uuid = m.group(1)
        self.assertRedirects(response, '/rentals/%s/' % uuid)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            '[Verleihtool] Your rental request, Guest User'
        )
        self.assertIn('Hello Guest User', mail.outbox[0].body)
        self.assertIn('* 1x My Item', mail.outbox[0].body)
        self.assertIn('/rentals/%s/' % uuid, mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].from_email, 'verleih@fs.tum.de')
        self.assertEqual(mail.outbox[0].to, ['guest@user.com'])

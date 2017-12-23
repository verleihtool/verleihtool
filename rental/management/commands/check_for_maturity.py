from django.core.management.base import BaseCommand
from rental.models import Rental
from django.utils.timezone import datetime, timedelta
from django.core.mail import send_mass_mail
from django.template import Context
from django.template.loader import render_to_string
import html2text


class Command(BaseCommand):

    @staticmethod
    def get_dmg_emailaddr_list(depot_managers):
        email_list = []
        for dmg in depot_managers:
            email_list.append(dmg.email)
        return email_list

    def get_mail_tuple(self, rental, interval):
        """
        Render the template for the rental and transform it to string tuple
        :param rental: the rental that is due
        :param interval: number of days twithin which a reminder email is to be sent
        :return: an email string tuple (first component: email for requester,
        second component: email for dmg)
        """
        mailcontext = Context({
            'firstname': rental.firstname,
            'lastname': rental.lastname,
            'email': rental.email,
            'start_date': rental.start_date,
            'return_date': rental.return_date,
            'uuid': rental.uuid,
            'itemrental_list': rental.itemrental_set.all(),
            'absoluteuri': 'http://127.0.0.1:1337/rentals/',
            'depotname': rental.depot.name
        })
        html_mail_to_requester = render_to_string('first-reminder-to-requester.html', mailcontext)
        html_mail_to_dmg = render_to_string('first-reminder-to-dmg.html', mailcontext)
        return (
            (
                '[Verleihtool] Your rental request from "%s" is due for %i days, %s %s!'
                % (rental.depot.name, interval, rental.firstname, rental.lastname),
                html2text.html2text(html_mail_to_requester),
                'verleih@fs.tum.de',
                [rental.email]
            ),
            (
                '[Verleihtool] Your rental request from "%s" is due for %i days, %s %s!'
                % (rental.depot.name, interval, rental.firstname, rental.lastname),
                html2text.html2text(html_mail_to_dmg),
                'verleih@fs.tum.de',
                self.get_dmg_emailaddr_list(rental.depot.managers)
            ),
        )

    @staticmethod
    def get_due_rentals(interval):
        return Rental.objects.filter(
            return_date=datetime.today - timedelta(days=interval),
            state='2'
        )

    def send_first_reminder(self):
        # todo set time interval externally by passing arguments to a method when setting cron job
        interval = 7
        due_since_interval_rentals = self.get_due_rentals(interval)
        for rental in due_since_interval_rentals:
            send_mass_mail(self.get_mail_tuple(rental, interval), fail_silently=True)

    def handle(self, *args, **options):
        self.send_first_reminder()

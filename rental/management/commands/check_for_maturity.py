from django.core.management.base import BaseCommand, CommandError
from rental.models import Rental
from django.utils.timezone import datetime, timedelta
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string


class Command(BaseCommand):
    """
    A command that sends a reminder email to requesters (and DMGs) whose rental
    has been due for a specific time interval.
    :author: Stefan
    """
    help = ('Sends a reminder email to all customers whose rentals '
            'have been due for a specified interval.')

    @staticmethod
    def get_dmg_emailaddr_list(depot_managers):
        email_list = []
        for dmg in depot_managers:
            email_list.append(dmg.email)
        return email_list

    def get_mail_tuple(self, due_rentals, interval):
        """
        Render the template for the rental and transform it to string tuple
        :param due_rentals: the rental that is due
        :param interval: number of days twithin which a reminder email is to be sent
        :return: an email string tuple (first component: email for requester,
        second component: email for dmg)
        """

        mail_tuple = ()

        for rental in due_rentals:
            subject_to_requester = \
                '[Verleihtool] %s %s\'s rental request from "%s" has been due for %i days!' \
                % (rental.firstname, rental.lastname, rental.depot.name, interval)
            message_to_requester = render_to_string(
                'rental/mails/first-reminder-to-requester.md',
                {'rental': rental}
            )
            subject_to_dmg = \
                '[Verleihtool] The rental request from "%s" has been due for %i days, %s %s!' \
                % (rental.depot.name, interval, rental.firstname, rental.lastname)
            message_to_dmg = render_to_string(
                'rental/mails/first-reminder-to-dmg.md',
                {'rental': rental}
            )

            mail_tuple += (
                (
                    subject_to_requester,
                    message_to_requester,
                    'verleih@fs.tum.de',
                    [rental.email]
                ),
                (
                    subject_to_dmg,
                    message_to_dmg,
                    'verleih@fs.tum.de',
                    self.get_dmg_emailaddr_list(rental.depot.managers)
                ),
            )

        return mail_tuple

    def add_arguments(self, parser):
        parser.add_argument('interval',
                            help='interval in days for email reminder after rental due date',
                            nargs=1, type=int)

    def handle(self, *args, **options):
        if len(options['interval']) > 1:
            raise CommandError('You can only specify one interval!')
        else:
            interval = int(options['interval'][0])
            due_rentals \
                = Rental.objects \
                .filter(return_date__lte=datetime.today() - timedelta(days=interval)) \
                .filter(state=Rental.STATE_APPROVED)
            send_mass_mail(self.get_mail_tuple(due_rentals, interval), fail_silently=True)

import markdown
import urllib
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.views import View
from depot.helpers import extract_item_quantities
from depot.models import Item
from rental.availability import Availability
from rental.models import Rental, ItemRental


class RentalCreateView(View):
    """
    Create a new rental object and assign the selected items to it

    When the object is successfully created, the user is redirected
    to the detail view of the new rental.
    If an error occurs, the message dictionary is stored in the
    current session and the user gets back to the edit view to
    correct their mistakes.

    :author: Florian Stamer
    """

    def post(self, request):
        data = request.POST

        user = request.user if request.user.is_authenticated else None

        try:
            # The transaction is cancelled if an unhandled exception occurs
            # in the following block
            with transaction.atomic():
                rental = self.create_rental(user, data)
                self.create_items(rental, data)

            # After transaction send a confirmation mail to the user
            self.send_confirmation_mail(request, rental)

            # Finally redirect the user to the rental page
            return redirect('rental:detail', rental_uuid=rental.uuid)
        except ValidationError as e:
            # Store the errors and the submitted data in the current session
            request.session['errors'] = e.message_dict
            request.session['data'] = data

            # Redirect to the form where the errors are displayed
            response = redirect('depot:create_rental', depot_id=data.get('depot_id'))
            response['Location'] += '?' + urllib.parse.urlencode({
                'start_date': data.get('start_date'),
                'return_date': data.get('return_date')
            })

            return response

    def create_rental(self, user, data):
        keys = (
            'firstname', 'lastname', 'depot_id', 'email', 'purpose', 'start_date', 'return_date'
        )
        rental = Rental(user=user, **{key: data.get(key) for key in keys})
        rental.full_clean()
        rental.save()
        # Refresh Rental object to fix issue with depot_id
        rental.refresh_from_db()
        return rental

    def create_items(self, rental, data):
        errors = {}

        item_quantities = extract_item_quantities(data)

        if not item_quantities:
            raise ValidationError({
                'item_quantities': 'The rental cannot be submitted without any items.'
            })

        item_list = Item.objects.filter(id__in=item_quantities.keys())

        availability = Availability(rental.start_date, rental.return_date, rental.depot_id)

        for item in item_list:
            intervals = availability.get_availability_intervals(item)

            try:
                available = min(intervals).value
                self.create_item_rental(rental, item, item_quantities[item.id], available)
            except ValidationError as e:
                for key, value in e:
                    errors['%s %s' % (item.name, key)] = value

        if errors:
            raise ValidationError(errors)

    def create_item_rental(self, rental, item, quantity, available):
        if quantity > available:
            raise ValidationError({
                'quantity': 'The quantity must not exceed the availability '
                            'of the item in the requested time frame.'
            })

        item_rental = ItemRental(
            rental=rental,
            item=item,
            quantity=quantity
        )
        item_rental.full_clean()
        item_rental.save()

    def send_confirmation_mail(self, request, rental):
        subject = ('[Verleihtool] Your rental request, %s %s' %
                   (rental.firstname, rental.lastname))
        message = render_to_string('rental/mails/confirmation.md', {
            'rental': rental
        }, request)

        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            to=[rental.email],
            cc=settings.CC_EMAIL,
        )

        email.attach_alternative(markdown.markdown(message), 'text/html')

        email.send()

from django.shortcuts import render, redirect, get_object_or_404

from .models import Rental, ItemRental
from django.db import transaction
from django.views.decorators.http import require_POST
import re
import html2text

from django.core.mail import send_mail
from django.template import Context
from django.template.loader import render_to_string


@require_POST
@transaction.atomic
def create(request):
    # get data
    data = request.POST

    params = (
        'name', 'depot_id', 'email', 'purpose', 'start_date', 'return_date'
    )

    user = request.user if request.user.is_authenticated else None

    # create Rental object
    rental = Rental(user=user, **{key: data.get(key) for key in params})
    rental.full_clean()
    rental.save()

    # create ItemRental objects
    for key, quantity in data.items():
        m = re.match(r'^item-([0-9]+)-quantity$', key)
        if m is not None and int(quantity) > 0:
            item = ItemRental(
                rental_id=rental.uuid,
                item_id=m.group(1),
                quantity=quantity
            )
            item.full_clean()
            item.save()

    p = re.compile('/(create)/')

    mailcontext = Context({
        'username': rental.name,
        'start_date': rental.start_date,
        'return_date': rental.return_date,
        'uuid': rental.uuid,
        'itemrental_list': rental.itemrental_set.all(),
        'absoluteuri': p.sub('/', request.build_absolute_uri())
    })

    html_content = render_to_string('rental_confirmation_email.html', mailcontext)
    plain_txt_mail = html2text.html2text(html_content)

    send_mail(
        'Your rental request, %s ' % rental.name,
        plain_txt_mail,
        'verleih@tool.de',
        [rental.email],
        html_message=html_content,
        fail_silently=True,
    )

    return redirect('rental:detail', rental_uuid=rental.uuid)


def detail(request, rental_uuid):
    rental = get_object_or_404(Rental, pk=rental_uuid)
    dmg = rental.depot.managed_by(request.user)
    item_list = rental.itemrental_set.all()
    if rental.state == Rental.STATE_PENDING:
        alert = "alert alert-info"
    elif rental.state == Rental.STATE_APPROVED:
        alert = "alert alert-success"
    elif rental.state == Rental.STATE_DECLINED:
        alert = "alert alert-danger"
    else:
        alert = "alert alert.warning"

    return render(request, 'rental/detail.html', {
        'rental': rental,
        'dmg': dmg,
        'item_list': item_list,
        'alert': alert,
    })


def update(request, rental_id):
    return render(request, 'rental/update.html')

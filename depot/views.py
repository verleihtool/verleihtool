from django.shortcuts import render, get_object_or_404
from .models import Depot, Item


def index(request):
    if request.user.is_superuser:
        depot_list = Depot.objects.all()
    else:
        depot_list = Depot.objects.filter(active=True)

    return render(request, 'depot/index.html', {
        'depot_list': depot_list
    })


def detail(request, depot_id):
    if request.user.is_superuser:
        depot = get_object_or_404(Depot, pk=depot_id)
    else:
        depot = get_object_or_404(Depot, pk=depot_id, active=True)

    if request.user.is_authenticated:
        item_list = depot.item_set.all()
    else:
        item_list = depot.item_set.filter(visibility=Item.VISIBILITY_PUBLIC)

    error_message = None
    if 'message' in request.session and request.session['message'] is not None:
        error_message = request.session['message']
        request.session.__delitem__('message')

    return render(request, 'depot/detail.html', {
        'depot': depot,
        'managed_by_user': depot.managed_by(request.user),
        'item_list': item_list,
        'error_message': error_message,
    })

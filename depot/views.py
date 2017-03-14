from django.shortcuts import render, get_object_or_404
from .models import Depot, Item

# Create your views here.

def index(request):
    depot_list = Depot.objects.all()
    context = {
        'depot_list': depot_list,
    }
    return render(request, 'depot/index.html', context)

def detail(request, depot_id):
    depot = get_object_or_404(Depot, pk=depot_id)
    if request.user.is_authenticated:
        item_list = depot.item_set.all()
    else:
        item_list = depot.item_set.filter(visibility=Item.VISIBILITY_PUBLIC)
    context = {
        'depot_name': depot.name,
        'item_list': item_list,
    }
    return render(request, 'depot/detail.html', context)

from django.contrib import admin

from .models import Depot, Item

# make depots modifiable by admin
admin.site.register(Depot)

# make items modifiable by admin
admin.site.register(Item)

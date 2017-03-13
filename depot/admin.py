from django.contrib import admin

from .models import Depot, Item

class ItemsInLine(admin.TabularInline):
    model = Item
    extra = 0

class DepotAdmin(admin.ModelAdmin):
    inlines = [ItemsInLine]

# make depots modifiable by admin
admin.site.register(Depot, DepotAdmin)

# make items modifiable by admin
admin.site.register(Item)

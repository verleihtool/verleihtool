from django.contrib import admin
from .models import Rental, ItemRental


class ItemRentalInline(admin.TabularInline):
    model = ItemRental
    extra = 0


class RentalAdmin(admin.ModelAdmin):
    inlines = [ItemRentalInline]


# Register your models here.
admin.site.register(Rental, RentalAdmin)

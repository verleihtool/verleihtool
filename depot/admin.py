from django.contrib import admin
from .models import Depot, Organization
from .admins.depot import DepotAdmin
from .admins.organization import OrganizationAdmin


# make organizations modifiable by admin
admin.site.register(Organization, OrganizationAdmin)

# make depots modifiable by admin
admin.site.register(Depot, DepotAdmin)

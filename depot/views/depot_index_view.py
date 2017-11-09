from django.shortcuts import render
from django.views import View
from depot.models import Organization


class DepotIndexView(View):
    """
    Show an index page of all organizations and their depots

    Only organization managers get a link to the admin interface of their
    organization so that they can change the name and add new depots.

    :author: Florian Stamer
    :author: Benedikt Seidl
    """

    def get(self, request):
        organization_depots = []

        for organization in Organization.objects.all():
            managed_by_user = organization.managed_by(request.user)
            depots = organization.active_depots.all()

            if depots:
                organization_depots.append({
                    'model': organization,
                    'managed_by_user': managed_by_user,
                    'depots': depots
                })

        return render(request, 'depot/index.html', {
            'organization_depots': organization_depots
        })

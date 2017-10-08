from depot import availability, helpers
from django.shortcuts import render
from django.views import View


class DepotCreateRentalView(View):
    """
    Show a form to create a new rental for the given depot

    :author: Benedikt Seidl
    """

    def get(self, request, depot_id):
        depot = helpers.get_depot_if_allowed(depot_id, request.user)

        # configure time frame
        start_date, return_date = helpers.get_start_return_date(request.GET)

        item_list = helpers.get_item_list(depot, request.user)
        item_availability_intervals = availability.get_item_availability_intervals(
            start_date, return_date, depot_id, item_list
        )

        availability_data = []
        for item, intervals in item_availability_intervals:
            availability_data.append((
                item,
                helpers.get_chart_data(intervals),
                availability.get_minimum_availability(intervals)
            ))

        errors = request.session.pop('errors', None)
        data = request.session.pop('data', {})

        return render(request, 'depot/create-rental.html', {
            'depot': depot,
            'show_visibility': depot.show_private_items(request.user),
            'availability_data': availability_data,
            'errors': errors,
            'data': data,
            'item_quantities': helpers.extract_item_quantities(data),
            'start_date': start_date,
            'return_date': return_date,
            'start_date_formatted': start_date.strftime('%Y-%m-%d %H:%M'),
            'return_date_formatted': return_date.strftime('%Y-%m-%d %H:%M')
        })

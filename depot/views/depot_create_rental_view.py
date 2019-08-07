from datetime import datetime, timedelta
from depot.helpers import get_depot_if_allowed, extract_item_quantities
from django.shortcuts import render
from django.views import View
from rental.availability import Availability


class DepotCreateRentalView(View):
    """
    Show a form to create a new rental for the given depot

    :author: Benedikt Seidl
    """

    def get(self, request, depot_id):
        depot = get_depot_if_allowed(depot_id, request.user)

        # configure time frame
        start_date, return_date = self.get_start_return_date(request.GET)

        item_list = depot.visible_items(request.user)

        availability = Availability(
            datetime.combine(start_date.date() - timedelta(days=1), datetime.min.time()),
            datetime.combine(return_date.date() + timedelta(days=1), datetime.min.time()),
            depot_id
        )

        availability_data = []

        for item in item_list:
            intervals = availability.get_availability_intervals(item)

            availability_data.append((
                item,
                self.get_chart_data(intervals),
                min(intervals).value
            ))

        errors = request.session.pop('errors', None)
        data = request.session.pop('data', {})

        return render(request, 'depot/create-rental.html', {
            'depot': depot,
            'show_visibility': depot.show_internal_items(request.user),
            'availability_data': availability_data,
            'errors': errors,
            'data': data,
            'item_quantities': extract_item_quantities(data),
            'start_date': start_date,
            'return_date': return_date,
            'start_date_formatted': start_date.strftime('%Y-%m-%d %H:%M'),
            'return_date_formatted': return_date.strftime('%Y-%m-%d %H:%M')
        })

    def get_start_return_date(self, data):
        """
        Return the start and return dates from the request

        If required data is missing or invalid, default values are returned.
        """

        try:
            start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d %H:%M')
        except (ValueError, TypeError):
            start_date = datetime.now() + timedelta(days=1)

        try:
            return_date = datetime.strptime(data.get('return_date'), '%Y-%m-%d %H:%M')
        except (ValueError, TypeError):
            return_date = start_date + timedelta(days=3)

        return (start_date, max(start_date, return_date))

    def get_chart_data(self, intervals):
        """
        Generate the data the JavaScript can render
        """

        data = []

        for interval in intervals:
            data.append({
                "x": interval.begin.isoformat(),
                "y": interval.value
            })
            data.append({
                "x": interval.end.isoformat(),
                "y": interval.value
            })

        return data

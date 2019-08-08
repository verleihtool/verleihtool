from django.db.models import Prefetch
from rental.models import ItemRental, Rental


class Interval:
    """
    An interval with a beginning, an end and an associated value.

    :author: Benedikt Seidl
    """

    def __init__(self, begin, end, value):
        self.begin = begin
        self.end = end
        self.value = value

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return (self.begin == other.begin
                and self.end == other.end
                and self.value == other.value)

    def __repr__(self):
        return '<Interval begin:"%s" end:"%s" value:%d>' % (self.begin, self.end, self.value)

    def __str__(self):
        return '[%s, %s] -> %d' % (self.begin, self.end, self.value)


class Availability:
    """
    Helper class to determine the availability of a list of items

    An item becomes only unavailable when it is parted of an approved rental
    request. All other items, especially in rental requests that are still
    pending, are considered available.

    :author: Leo Tappe
    """

    def __init__(self, start_date, return_date, depot_id,
                 conflicting_states=[Rental.STATE_APPROVED]):
        self.start_date = start_date
        self.return_date = return_date
        self.depot_id = depot_id
        self.conflicting_states = conflicting_states

    def get_availability_intervals(self, item):
        """
        Split the given time frame into a sequence of intervals
        with the corresponding amount of available elements.

        :author: Leo Tappe

        :param item: the item that you want to rent
        :return: a list of lists of the form [from, to, num_available]
        """

        interval_borders = []
        intervals = []

        rentals = Rental.objects.filter(
            start_date__lt=self.return_date,
            return_date__gt=self.start_date,
            depot_id=self.depot_id,
            state__in=self.conflicting_states,
            items=item
        ).prefetch_related(
            Prefetch(
                'itemrental_set',
                queryset=ItemRental.objects.filter(item=item),
                to_attr='relevant_rental'
            )
        )

        # collect all the datetimes where a relevant rental starts / gets returned
        for rental in rentals:
            if rental.start_date > self.start_date:
                interval_borders.append(rental.start_date)
            if rental.return_date < self.return_date:
                interval_borders.append(rental.return_date)

        # insert start and end date
        interval_borders.append(self.start_date)
        interval_borders.append(self.return_date)

        # sort these points
        interval_borders.sort()

        # create intervals, initialize with full availability
        for begin, end in zip(interval_borders, interval_borders[1:]):
            intervals.append(Interval(begin, end, item.quantity))

        # for each rental, modify availability during occupied intervals accordingly
        for rental in rentals:
            for interval in intervals:
                if rental.start_date < interval.end and rental.return_date > interval.begin:
                    interval.value -= rental.relevant_rental[0].quantity

        return intervals

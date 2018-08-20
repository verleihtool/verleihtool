from rental.models import Rental


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
        return (self.begin == other.begin and
                self.end == other.end and
                self.value == other.value)

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

        self.rentals = Rental.objects.filter(
            start_date__lt=self.return_date,
            return_date__gt=self.start_date,
            depot_id=self.depot_id,
            state__in=conflicting_states
        )

    def get_availability_intervals(self, item):
        """
        Split the given time frame into a sequence of intervals
        with the corresponding amount of available elements.

        :author: Leo Tappe

        :param item: the item that you want to rent
        :return: a list of lists of the form [from, to, num_available]
        """

        relevant_rentals = []
        interval_borders = []
        intervals = []

        # collect all the datetimes where a relevant rental starts / gets returned
        for rental in self.rentals:
            if (rental.start_date < self.return_date and
                    rental.return_date > self.start_date and
                    item in rental.items.all()):
                if rental.start_date > self.start_date:
                    interval_borders.append(rental.start_date)
                if rental.return_date < self.return_date:
                    interval_borders.append(rental.return_date)
                relevant_rentals.append(rental)

        # sort these points (ascending)
        interval_borders.sort()

        # append / prepend start and end date if necessary
        interval_borders.insert(0, self.start_date)
        interval_borders.append(self.return_date)

        # create intervals, initialize with full availability
        for i in range(len(interval_borders) - 1):
            intervals.append(Interval(interval_borders[i], interval_borders[i + 1], item.quantity))

        # for each rental, modify availability during occupied intervals accordingly
        for rental in relevant_rentals:
            item_rental = rental.itemrental_set.get(item=item)
            for interval in intervals:
                if rental.start_date < interval.end and rental.return_date > interval.begin:
                    interval.value -= item_rental.quantity

        return intervals

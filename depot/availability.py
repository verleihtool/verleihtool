from rental.models import Rental


def get_item_availability_list(start_date, return_date, depot_id, item_list):
    """
    Calculate availability for each item in item_list

    :author: Leo Tappe
    """

    rentals = Rental.objects.filter(
        start_date__lt=return_date,
        return_date__gt=start_date,
        depot_id=depot_id,
        state=Rental.STATE_APPROVED
    )
    availability_list = []

    for item in item_list:
        intervals = get_availability_intervals(
            start_date, return_date, item, rentals
        )
        availability_list.append(
            (item, get_maximum_availability(intervals))
        )

    return availability_list


def get_availability_intervals(start, end, item, rentals):
    """
    Split the given time frame into a sequence of intervals
    with the corresponding amount of available elements.

    :author: Leo Tappe

    :param start: the beginning of the time frame
    :param end: the end of the time frame
    :param item: the item that you want to rent
    :param rentals: a list of all rentals
    :return: a list of lists of the form [from, to, num_available]
    """

    relevant_rentals = []
    interval_borders = []
    intervals = []

    # collect all the datetimes where a relevant rental starts / gets returned
    for rental in rentals:
        if (rental.start_date < end and
                rental.return_date > start and
                item in rental.items.all()):
            if rental.start_date > start:
                interval_borders.append(rental.start_date)
            if rental.return_date < end:
                interval_borders.append(rental.return_date)
            relevant_rentals.append(rental)

    # sort these points (ascending)
    interval_borders.sort()

    # append / prepend start and end date if necessary
    interval_borders.insert(0, start)
    interval_borders.append(end)

    # create intervals, initialize with full availability
    for i in range(len(interval_borders) - 1):
        intervals.append([interval_borders[i], interval_borders[i + 1], item.quantity])

    # for each rental, modify availability during occupied intervals accordingly
    for rental in relevant_rentals:
        item_rental = rental.itemrental_set.get(item=item)
        for interval in intervals:
            if rental.start_date < interval[1] and rental.return_date > interval[0]:
                interval[2] -= item_rental.quantity

    return intervals


def get_maximum_availability(intervals):
    """
    Get the maximum quantity that is available in every interval

    :author: Leo Tappe

    :param intervals: the intervals for which availability has been calculated
    :return: the minimum num_available value across all intervals
    """

    min_interval = min(intervals, key=lambda x: x[2])
    return min_interval[2]

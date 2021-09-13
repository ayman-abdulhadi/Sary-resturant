from django.db.models import F, Func, Value, CharField
import datetime
from restaurant.local_requirements.interval import Interval, IntervalSet


restaurant_start_time = datetime.timedelta(hours=13).seconds
restaurant_end_time = datetime.timedelta(hours=23, minutes=59).seconds


def normalize_table(table):
    today = datetime.date.today()
    qs = table.reservations.filter(
        start_time__year=today.year,
        start_time__month=today.month,
        start_time__day=today.day
    )
    times = qs.annotate(
        formatted_start_time=Func(
            F('start_time'),
            Value('HH:MM AM'),
            function='to_char',
            output_field=CharField()
        ),
        formatted_end_time=Func(
            F('end_time'),
            Value('HH:MM AM'),
            function='to_char',
            output_field=CharField()
        )
    ).values_list('formatted_start_time', 'formatted_end_time')
    times = sorted(list(times))

    times_in_seconds = []
    for i in times:
        s = datetime.datetime.strptime(i[0], '%I:%M %p') - datetime.datetime(1900, 1, 1)
        t = datetime.datetime.strptime(i[1], '%I:%M %p') - datetime.datetime(1900, 1, 1)
        times_in_seconds.append(Interval(s.total_seconds(), t.total_seconds()))
    bigger_intv = IntervalSet(
            [Interval(restaurant_start_time, restaurant_end_time)]
        )
    small_intv = IntervalSet(times_in_seconds)
    intervals = bigger_intv - small_intv
    humanize_intervals = [(i.lower_bound, i.upper_bound) for i in intervals.intervals]

    output_times = []
    for i in humanize_intervals:
        start = datetime.datetime.strptime(
            str(datetime.timedelta(seconds=i[0])),
            '%H:%M:%S'
        ).strftime('%I:%M %p')
        end = datetime.datetime.strptime(
            str(datetime.timedelta(seconds=i[1])),
            '%H:%M:%S'
        ).strftime('%I:%M %p')
        output_times.append(f'{start} - {end}')
    return output_times


def check_available_slots(queryset, num_of_seats):
    if int(num_of_seats) <= 0:
        return []
    tables = queryset.filter(
        num_of_seats__gte=num_of_seats,
    ).order_by('num_of_seats')
    serialized_data = [{f'table #{table.number}': normalize_table(table)} for table in tables]
    return serialized_data


def reformat(time):
    return datetime.datetime.strptime(
        time, '%I:%M %p'
    ).strftime('%H:%M %p')


def in_between(time, start, end):
    return start <= time <= end


def check_time_between(time, intervals):
    times = [(reformat(i.split(' - ')[0]), reformat(i.split(' - ')[1])) for i in intervals]
    for interval in times:
        if in_between(time[0], interval[0], interval[1]) and \
                in_between(time[1], interval[0], interval[1]):
            return True
    return False

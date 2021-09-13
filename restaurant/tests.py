from django.test import TestCase
from restaurant.models import Table, Reservation
from restaurant.serializers import (
    TableSerializer, ReservationDetailSerializer
)
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import datetime


TABLE_URL = reverse('restaurant:table-list')
AVAILABLE_SLOTS_URL = reverse('restaurant:table-check-available-slots')
RESERVATIONS_URL = reverse('restaurant:reservation-list')
TODAY_RESERVATIONS_URL = reverse('restaurant:reservation-today-reservations')


def table_detail_url(table_number):
    return reverse('restaurant:table-detail', args=[table_number])


def reservation_detail_url(reservation_id):
    return reverse('restaurant:reservation-detail', args=[reservation_id])


def sample_table(number=33, num_of_seats=7):
    default = {
        'number': number,
        'num_of_seats': num_of_seats
    }
    return Table.objects.create(**default)


def sample_reservation(
            table_obj,
            start_time=datetime.datetime.now(),
            end_time=datetime.datetime.now() + datetime.timedelta(hours=2)
        ):
    default = {
        'table': table_obj,
        'start_time': start_time,
        'end_time': end_time
    }
    return Reservation.objects.create(**default)


class PublicRestaurantAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res_1 = self.client.get(TABLE_URL)
        res_2 = self.client.get(RESERVATIONS_URL)
        self.assertEqual(res_1.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res_2.status_code, status.HTTP_401_UNAUTHORIZED)


class RestaurantAPITests(TestCase):

    def setUp(self):
        self.admin_user = get_user_model().objects.create(
            employee_number='9999',
            password='pass123',
            name='test',
            role='Admin'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.admin_user)

    def test_list_tables(self):
        sample_table()
        sample_table(87, 11)
        res = self.client.get(TABLE_URL)
        tables = Table.objects.all()
        serializer = TableSerializer(tables, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_table_detail_view(self):
        table = sample_table()
        url = table_detail_url(table.number)
        res = self.client.get(url)
        serializer = TableSerializer(table)
        self.assertEqual(res.data, serializer.data)

    def test_create_table(self):
        payload = {
            'number': 12,
            'num_of_seats': 3
        }
        res = self.client.post(TABLE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        table = Table.objects.get(number=res.data['number'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(table, key))

    def test_delete_table(self):
        table = sample_table()
        url = table_detail_url(table.number)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_available_slots(self):
        table = sample_table()
        payload = {
            'num_of_seats': 5
        }
        res = self.client.post(AVAILABLE_SLOTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        exp = {
            "ordered_available_slots": [
                {
                    f"table #{table.number}": [
                        "01:00 PM - 11:59 PM"
                    ]
                }
            ]
        }
        self.assertEqual(res.data, exp)

    def test_list_reservations(self):
        table = sample_table()
        sample_reservation(table_obj=table)
        res = self.client.get(RESERVATIONS_URL)
        reservations = Reservation.objects.all()
        serializer = ReservationDetailSerializer(reservations, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_today_reservations(self):
        table = sample_table()
        sample_reservation(table_obj=table)
        res = self.client.get(TODAY_RESERVATIONS_URL)
        reservations = Reservation.objects.all()
        serializer = ReservationDetailSerializer(reservations, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_reservation_detail_view(self):
        table = sample_table()
        reservation = sample_reservation(table_obj=table)
        url = reservation_detail_url(reservation.id)
        res = self.client.get(url)
        serializer = ReservationDetailSerializer(reservation)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_reservation(self):
        table = sample_table()
        payload = {
            'table': table,
            'start_time': "02:45 PM",
            'end_time': "04:30 PM"
        }
        res = self.client.post(RESERVATIONS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        payload.update({'table': table.number})
        self.assertEqual(res.data, payload)

    def test_delete_reservation(self):
        table = sample_table()
        reservation = sample_reservation(table_obj=table)
        url = reservation_detail_url(reservation.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_reservations_by_number(self):
        rsv_1 = sample_reservation(table_obj=sample_table())
        sample_reservation(table_obj=sample_table(11, 4))
        filter_by_table_number = RESERVATIONS_URL + \
            f'?table_number={rsv_1.table.number}'
        res = self.client.get(filter_by_table_number)
        reservations = Reservation.objects.filter(
            table__number=rsv_1.table.number
        )
        serializer = ReservationDetailSerializer(reservations, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_filter_reservations_by_order(self):
        sample_reservation(table_obj=sample_table())
        sample_reservation(table_obj=sample_table(11, 4))
        filter_by_asc_order = RESERVATIONS_URL + '?time_order=asc'
        filter_by_dsc_order = RESERVATIONS_URL + '?time_order=dsc'
        res_1 = self.client.get(filter_by_asc_order)
        res_2 = self.client.get(filter_by_dsc_order)
        reservations_1 = Reservation.objects.order_by('start_time')
        reservations_2 = Reservation.objects.order_by('-start_time')
        serializer_1 = ReservationDetailSerializer(reservations_1, many=True)
        serializer_2 = ReservationDetailSerializer(reservations_2, many=True)
        self.assertEqual(res_1.status_code, status.HTTP_200_OK)
        self.assertEqual(res_1.data['results'], serializer_1.data)
        self.assertEqual(res_2.status_code, status.HTTP_200_OK)
        self.assertEqual(res_2.data['results'], serializer_2.data)

    def test_filter_reservations_by_date_range(self):
        start = datetime.datetime(2021, 9, 10, 15, 30)
        end = datetime.datetime(2021, 9, 10, 18)
        sample_reservation(
            table_obj=sample_table(),
            start_time=start,
            end_time=end
        )
        sample_reservation(
            table_obj=sample_table(11, 4),
            start_time=datetime.datetime(2021, 9, 22, 14),
            end_time=datetime.datetime(2021, 9, 22, 16)
        )
        filter_by_table_number = RESERVATIONS_URL + \
            '?date_range=9-9-2021,15-9-2021'
        res = self.client.get(filter_by_table_number)
        reservations = Reservation.objects.filter(
            start_time__date__range=[start.date(), end.date()]
        )
        serializer = ReservationDetailSerializer(reservations, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

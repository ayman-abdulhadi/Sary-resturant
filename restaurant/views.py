from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from restaurant.serializers import (
    TableSerializer, ReservationSerializer, ReservationDetailSerializer,
    CheckAvailableSlotsSerializer
)
from restaurant.models import Table, Reservation
from restaurant.permissions import IsAdminOrNone
from restaurant.utils import check_available_slots
import datetime


class TabletViewSet(ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    permission_classes = (IsAuthenticated, IsAdminOrNone)
    lookup_field = 'number'
    http_method_names = ['get', 'post', 'delete']

    def get_serializer_class(self):
        if self.action in ['check_available_slots']:
            return CheckAvailableSlotsSerializer
        return self.serializer_class

    def destroy(self, request, number=None):
        table = self.get_object()
        if table.reservations.all():
            response = {
                'message': 'Not permitted, the table has reservations.'
            }
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        else:
            table.delete()
            response = {'message': 'Deleted successfully.'}
            return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='check-available-slots')
    def check_available_slots(self, request):
        queryset = self.queryset
        num_of_seats = request.data['num_of_seats']
        if num_of_seats.isdigit():
            slots = check_available_slots(queryset, num_of_seats)
            return Response(
                {'ordered_available_slots': slots},
                status=status.HTTP_200_OK
            )
        return Response(
            {'message': 'Only digits are allowed.'},
            status=status.HTTP_403_FORBIDDEN
        )


class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationDetailSerializer
    http_method_names = ['get', 'post', 'delete']

    def get_permissions(self):
        if self.action in ['list']:
            self.permission_classes = (IsAdminOrNone,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super(ReservationViewSet, self).get_permissions()

    def get_queryset(self):
        queryset = Reservation.objects.all()

        if self.request.user.role == 'Admin':
            time_order = self.request.query_params.get('time_order', 0)
            if time_order:
                if time_order == 'asc':
                    queryset = queryset.order_by('start_time')
                elif time_order == 'dsc':
                    queryset = queryset.order_by('-start_time')

            table_number = self.request.query_params.get('table_number', 0)
            if table_number:
                queryset = queryset.filter(table__number=table_number)

            date_range = self.request.query_params.get('date_range', 0)
            if date_range:
                try:
                    start = datetime.datetime.strptime(
                                date_range.split(',')[0], '%d-%m-%Y'
                            ).date()
                    end = datetime.datetime.strptime(
                            date_range.split(',')[1], '%d-%m-%Y'
                        ).date()
                    queryset = queryset.filter(
                        start_time__date__range=[start, end]
                    )
                except Exception as e:
                    print(e)
        return queryset

    def get_serializer_class(self):
        if self.action in ['post', 'create']:
            return ReservationSerializer
        return self.serializer_class

    def destroy(self, request, pk=None):
        reservation = self.get_object()
        if reservation.start_time.date() == datetime.date.today():
            reservation.delete()
            response = {'message': 'Deleted Successfully.'}
            return Response(response, status=status.HTTP_200_OK)
        response = {'message': "You can't delete a reservation from the past."}
        return Response(response, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['GET'], url_path='today-reservations')
    def today_reservations(self, request):
        today = datetime.date.today()
        query_set = self.queryset.filter(
            start_time__year=today.year,
            start_time__month=today.month,
            start_time__day=today.day
        )
        serializer = self.serializer_class(
            query_set,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

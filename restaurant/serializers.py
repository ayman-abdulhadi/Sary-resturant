from django.core.exceptions import ValidationError
from rest_framework import serializers
from restaurant.models import Table, Reservation
from restaurant.utils import normalize_table, check_time_between
import datetime
from drf_custom_related_field import CustomRelatedField


class TableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = ['number', 'num_of_seats']


class ReservationDetailSerializer(serializers.ModelSerializer):
    table_number = serializers.SerializerMethodField()
    start_time = serializers.DateTimeField(format='%I:%M %p')
    end_time = serializers.DateTimeField(format='%I:%M %p')

    def get_table_number(self, obj):
        return obj.table.number

    class Meta:
        model = Reservation
        fields = ['pk', 'table_number', 'start_time', 'end_time']


class ReservationSerializer(serializers.Serializer):
    table = CustomRelatedField(
                queryset=Table.objects.all(),
                field_name='number',
                required=True
            )
    start_time = serializers.TimeField(
                format='%I:%M %p',
                input_formats=['%I:%M %p']
            )
    end_time = serializers.TimeField(
                format='%I:%M %p',
                input_formats=['%I:%M %p']
            )

    def create(self, validated_data):
        try:
            table = validated_data.get('table')
            start_time = validated_data.pop('start_time')
            end_time = validated_data.pop('end_time')
            s_time = start_time.strftime('%H:%M %p')
            e_time = end_time.strftime('%H:%M %p')
            times = normalize_table(table)
            is_valid = check_time_between((s_time, e_time), times)
            if not is_valid:
                raise ValidationError(
                    'Invalid start or end time, please check available slots.'
                )
            today = datetime.datetime.now()
            validated_data['start_time'] = today.replace(
                hour=start_time.hour,
                minute=start_time.minute,
                second=start_time.second
            )
            validated_data['end_time'] = today.replace(
                hour=end_time.hour,
                minute=end_time.minute,
                second=end_time.second
            )
            instance = Reservation.objects.create(**validated_data)
            instance.start_time = start_time
            instance.end_time = end_time
            return instance
        except Exception as e:
            raise ValidationError(e)


class CheckAvailableSlotsSerializer(serializers.Serializer):
    num_of_seats = serializers.IntegerField(required=True)

from django.contrib import admin
from restaurant.models import Table, Reservation


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'num_of_seats']
    search_fields = ['number']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['table', 'start_time', 'end_time']
    list_filter = ['table']

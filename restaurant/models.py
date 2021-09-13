from django.db import models


class Table(models.Model):
    SEATS_CHOICES = tuple(zip(range(1, 13), range(1, 13)))

    number = models.IntegerField(
                unique=True,
                error_messages={
                    'unique':
                    "A table with that number already exists."
                }
            )
    num_of_seats = models.IntegerField(choices=SEATS_CHOICES, default=1)

    def __str__(self):
        return str(self.number)


class Reservation(models.Model):
    table = models.ForeignKey(
                Table,
                related_name='reservations',
                on_delete=models.CASCADE
            )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f'reserver from {self.start_time} to {self.end_time}'

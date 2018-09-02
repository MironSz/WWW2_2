import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


# Create your models here.


class Airline(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Plane(models.Model):
    registration_num = models.CharField(max_length=200)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    seats = models.IntegerField(default=20)

    def clean(self):
        super().clean()
        if self.seats < 1:
            raise ValidationError("Number of seats must be a positive number.")

    def __str__(self):
        return self.registration_num


class Airport(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Crew(models.Model):
    captain_name = models.CharField(max_length=200)
    captain_surname = models.CharField(max_length=200)

    def __str__(self):
        return self.captain_name + ' ' + self.captain_surname

    class Meta:
        unique_together = ('captain_name', 'captain_surname',)


class Flight(models.Model):
    departure_airport = models.ForeignKey(Airport, related_name='departure', on_delete=models.CASCADE);
    arrival_airport = models.ForeignKey(Airport, related_name='arrival', on_delete=models.CASCADE);
    departure_time = models.DateTimeField("Departure time")
    arrival_time = models.DateTimeField("Arrival time")
    plane = models.ForeignKey(Plane, on_delete=models.CASCADE)
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, null=True, blank=True, default=None)

    def __str__(self):
        return self.plane.airline.__str__() + "/" + self.plane.__str__() + " flight nr " + self.id.__str__()

    def clean(self):
        super().clean()
        if Flight.objects.filter(plane=self.plane, departure_time__day=self.departure_time.day,
                                 departure_time__month=self.departure_time.month,
                                 departure_time__year=self.departure_time.year, ).count() >= 4:
            raise ValidationError("This plane has already 4 flights this day.")

        if self.arrival_time <= self.departure_time:
            raise ValidationError("Arrival time must be after departure time.")

        for fl in Flight.objects.filter(plane=self.plane):
            if self.departure_time < fl.departure_time < self.arrival_time or \
                    self.departure_time < fl.arrival_time < self.arrival_time:
                raise ValidationError("This plane already has a flight in this time.")

        if self.crew is not None:
            for fl in Flight.objects.filter(crew=self.crew):
                if self.departure_time <= fl.departure_time <= self.arrival_time or \
                        self.departure_time <= fl.arrival_time <= self.arrival_time:
                    raise ValidationError("This crew has already flight at the same time.")


class Passenger(models.Model):
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    seats = models.IntegerField(default=1)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + " " + self.surname

    def clean(self):
        super().clean()
        if self.seats < 1:
            raise ValidationError("Number of seats must ba a positive integer.")
        if Passenger.objects.filter(name=self.name, surname=self.surname, flight=self.flight).count() > 0:
            raise ValidationError(_("Such passenger already exists."))

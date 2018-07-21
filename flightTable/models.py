import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.


class Airline(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Plane(models.Model):
    registration_num = models.CharField(max_length=200)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    seats = models.IntegerField(default=20)

    def __str__(self):
        return self.registration_num


class Airport(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Passenger(models.Model):
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    def __str__(self):
        return self.name+" "+self.surname

class Flight(models.Model):
    departure_airport = models.ForeignKey(Airport, related_name='departure',on_delete=models.CASCADE);
    arrival_airport = models.ForeignKey(Airport, related_name='arrival',on_delete=models.CASCADE);
    departure_time = models.DateTimeField("Departure time")
    arrival_time = models.DateTimeField("Arrival time")
    plane = models.ForeignKey(Plane, on_delete=models.CASCADE)
    passenger = models.ManyToManyField(Passenger)
    def __str__(self):
        return self.plane.airline.__str__()+ "/"+self.plane.__str__()+" flight nr "+self.id.__str__()






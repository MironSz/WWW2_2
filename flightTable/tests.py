# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.test import TestCase, RequestFactory

from flightTable.models import Crew, Flight, Airport, Plane, Airline
import datetime
from django.core import serializers
import json


class ApiTest(TestCase):

    def setUp(self):
        self.password = 'password123'
        self.user = User.objects.create_user(username='john',
                                             email='jlennon@beatles.com',
                                             password=self.password)
        self.user.save()
        self.crew = Crew(captain_name="A1", captain_surname="B1")
        self.crew.save()
        self.crew2 = Crew(captain_name="A2", captain_surname="B2")
        self.crew2.save()
        self.airport1 = Airport(name="Airport1")
        self.airport1.save()
        self.airport2 = Airport(name="Airport2")
        self.airport2.save()
        self.airline1 = Airline(name="Airline1")
        self.airline1.save()
        self.departure_time = datetime.datetime(year=2015, month=5, day=13, hour=12, minute=15)
        self.arrival_time = datetime.datetime(year=2015, month=5, day=13, hour=17, minute=15)
        self.plane = Plane(registration_num="1", airline=self.airline1)
        self.plane.save()
        self.flight = Flight(arrival_airport=self.airport1, departure_airport=self.airport2,
                             plane=self.plane,
                             crew=self.crew,
                             arrival_time=self.arrival_time, departure_time=self.departure_time)
        self.flight.save()

    def test_get_crews_on_day(self):
        response = self.client.get('/api/flights_and_crews/', data={
            'day': self.departure_time.day,
            'month': self.departure_time.month,
            'year': self.departure_time.year,
        })
        expected = []
        expected.append({'flightId': self.flight.id,
                         'crew': self.flight.crew.captain_name + " " + self.flight.crew.captain_surname,
                         "departure airport": self.flight.departure_airport.__str__(),
                         "arrival airport": self.flight.arrival_airport.__str__()})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, JsonResponse({'crews': expected}).content)

    def test_change_crew_success(self):
        json_data = {
            'captain_name': self.crew2.captain_name,
            'flight_id': self.flight.id,
            'captain_surname': self.crew2.captain_surname,
            'username': self.user.username,
            'password': self.password,
        }
        response = self.client.generic('POST', '/api/change_crew/', json.dumps(json_data))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.crew2, Flight.objects.first().crew)

    def test_change_crew_fail(self):
        flight = Flight(arrival_airport=self.airport1, departure_airport=self.airport2,
                        plane=self.plane,
                        crew=self.crew2,
                        arrival_time=self.arrival_time + datetime.timedelta(hours=1),
                        departure_time=self.departure_time + datetime.timedelta(hours=1))
        flight.save()

        json_data = {
            'captain_name': self.crew.captain_name,
            'flight_id': flight.id,
            'captain_surname': self.crew.captain_surname,
            'username': self.user.username,
            'password': self.password,
        }
        response = self.client.generic('POST', '/api/change_crew/', json.dumps(json_data))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.crew2, Flight.objects.filter(id=flight.id).first().crew)  # unchanged

import datetime

from django.db.models.functions import Concat
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics

from flightTable.forms import RegistrationForm, AddPassengerToFlightForm
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, login as login_to_session
from django.contrib.auth.models import User
from .models import Flight, Passenger, Airport, Airline, Plane, Crew
from .serializers import CrewSerializers
import django_tables2 as tables
from django.db.models import Value
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
import json


def check_tags(tags, request):
    for tag in tags:
        if tag not in request.GET:
            print(tag)
            raise PermissionDenied("missing " + tag)


@require_GET
@csrf_exempt
def get_crews(request):
    check_tags(tags=['day', 'month', 'year'], request=request)

    date = datetime.date(year=int(request.GET['year']), month=int(request.GET['month']),
                         day=int(request.GET['day']))

    def get_crew_or_none(flight):
        try:
            return flight.crew.captain_name + " " + flight.crew.captain_surname
        except AttributeError:
            return ""

    response = []
    for flight in list(Flight.objects.all()):
        if flight.departure_time.date() <= date <= flight.arrival_time.date():
            response.append(
                {'flightId': flight.id,
                 'crew': get_crew_or_none(flight=flight),
                 "departure airport": flight.departure_airport.__str__(),
                 "arrival airport": flight.arrival_airport.__str__()})
    return JsonResponse({'crews': response})


@require_GET
@csrf_exempt
def login_rest(request):
    check_tags(tags=['password', 'username'], request=request)
    username = request.GET.get('username')
    password = request.GET.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        return JsonResponse({"success": True})

    else:
        return JsonResponse({"success": False})


@require_POST
@csrf_exempt
def change_crew(request):
    received_json_data = json.loads(request.body.decode("utf-8"))
    try:
        tags = ['captain_name', 'captain_surname', 'username', 'password', 'flight_id', ]
        for tag in tags:
            if tag not in received_json_data:
                raise ValidationError("Missing " + tag + " argument")
        username = received_json_data['username']
        password = received_json_data['password']
        captain_name = received_json_data['captain_name']
        captain_surname = received_json_data['captain_surname']
        flight_id = received_json_data['flight_id']
        user = authenticate(username=username, password=password)
        if user is not None:
            try:
                crew = Crew.objects.get(captain_surname=captain_surname, captain_name=captain_name)
            except Exception as e:
                raise ValidationError("Such crew does not exist")
            try:
                flight = Flight.objects.get(id=flight_id)
            except Exception as e:
                raise ValidationError("Such flight does not exist")

            flight.crew = crew

            flight.full_clean()
            flight.save()

        else:
            raise ValidationError("Only logged users may change crews assignment")

    except ValidationError as e:
        try:
            return JsonResponse({"success": False, "error": e.message})
        except Exception:
            return JsonResponse({"success": False, "error": "This crew has already flight at this time."})

    return JsonResponse({"success": True})

@csrf_exempt
@require_POST
def login(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        login_to_session(request, user)
    else:
        error = True
    return render(request, 'flightTable/login.html', locals())

@require_POST
@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=request.POST['username'],
                                            password=request.POST['password'])
            login_to_session(request, user)
            return redirect('main')
    else:
        form = RegistrationForm()
    return render(request, 'flightTable/register.html', locals())


@csrf_exempt
def flight(request, flightId):
    fl = get_object_or_404(Flight, id=flightId)
    passengers = Passenger.objects.filter(flight=fl)
    seatsRemaining = fl.plane.seats
    for passenger in passengers:
        seatsRemaining -= passenger.seats

    if request.user.is_authenticated:
        if request.method == 'POST':
            addPassengerForm = AddPassengerToFlightForm(request.POST, initial={"seats": 1},
                                                        seatsRemaining=seatsRemaining)
            addPassengerForm.full_clean()
            if addPassengerForm.is_valid():
                passenger = addPassengerForm.save(commit=False)
                name = request.POST.get('name')
                surname = request.POST.get('surname')
                flight = fl
                seats = request.POST.get("seats")

                if Passenger.objects.filter(name=name, surname=surname, flight=flight).exists():
                    passenger = Passenger.objects.filter(name=passenger.name,
                                                         surname=passenger.surname).first()
                    passenger.seats += int(seats)
                    passenger.save()
                else:
                    passenger = Passenger(name=name, surname=surname, seats=seats, flight=flight)
                    passenger.save()

                return redirect('flight', flightId)
        else:
            addPassengerForm = AddPassengerToFlightForm(initial={"seats": 1},
                                                        seatsRemaining=seatsRemaining)

    return render(request, 'flightTable/flight.html', locals())


class SimpleTable(tables.Table):
    edit_entries = tables.TemplateColumn('<a href="/flight/{{record.id}}">Add passengers</a>')

    class Meta:
        model = Flight
        attrs = {'class': 'table'}


def simple_list(request):
    if "sort" in request.GET and request.GET.get("sort", "") != "edit_entries":
        queryset = Flight.objects.all().order_by(request.GET.get("sort", ""))
    else:
        queryset = Flight.objects.all()

    table = SimpleTable(queryset)
    table.paginate(page=request.GET.get('page', 1), per_page=25)
    return render(request, 'flightTable/flight_list.html', {'table': table})


def populate_database(n):
    user = User.objects.create_user(username='user',
                                    email='jlennon@beatles.com',
                                    password="password123")
    user.save()
    airport1 = Airport(name="MIMUW")
    airport1.save()

    airport2 = Airport(name="PG")
    airport2.save()

    airport3 = Airport(name="MINIPW")
    airport3.save()

    airports = [airport1, airport2, airport3]

    crews = []
    for i in range(n):
        crew = Crew(captain_name="A" + i.__str__(), captain_surname="B" + i.__str__())
        crew.save()
        crews.append(crew)

    for i in range(n):
        airline = Airline(name="airline nr" + i.__str__())
        airline.save()
        plane = Plane(airline=airline, registration_num="rn" + i.__str__(), seats=20 + i % 11)
        delta = datetime.timedelta(days=1, hours=i)
        today = datetime.datetime.now()
        date = datetime.datetime.now() + delta
        plane.save()
        for j in range(n):
            start = today + j * delta
            finnish = start + datetime.timedelta(hours=i % 4 + 6, minutes=32 * (j % 10))
            flight = Flight(departure_airport=airports[j % 3],
                            arrival_airport=airports[(j + 1) % 3],
                            departure_time=start, arrival_time=finnish,
                            plane=plane)
            flight.save()

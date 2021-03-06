import datetime

from django.shortcuts import render, redirect, get_object_or_404
from flightTable.forms import RegistrationForm,AddPassengerToFlightForm
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login as login_to_session
from django.contrib.auth.models import User
from .models import Flight, Passenger, Airport, Airline, Plane

import django_tables2 as tables

@require_POST
def login(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        login_to_session(request, user)
    else:
        error = True
    return render(request, 'flightTable/login.html', locals())


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=request.POST['username'], password=request.POST['password'])
            login_to_session(request, user)
            return redirect('main')
    else:
        form = RegistrationForm()
    return render(request, 'flightTable/register.html', locals())


#@csrf_exempt
def flight(request, flightId):
    fl = get_object_or_404(Flight, id=flightId)
    passengers = Passenger.objects.filter(flight=fl)
    seatsRemaining = fl.plane.seats
    for passenger in passengers:
        seatsRemaining -= passenger.seats

    if request.user.is_authenticated:
        if request.method == 'POST':
            addPassengerForm = AddPassengerToFlightForm(request.POST,initial={"seats": 1}, seatsRemaining=seatsRemaining)
            addPassengerForm.full_clean()
            if addPassengerForm.is_valid():
                passenger = addPassengerForm.save(commit=False)
                name = request.POST.get('name')
                surname = request.POST.get('surname')
                flight = fl
                seats = request.POST.get("seats")

                if Passenger.objects.filter(name=name, surname=surname, flight=flight).exists():
                    passenger = Passenger.objects.filter(name = passenger.name,surname=passenger.surname).first()
                    passenger.seats += int(seats)
                    passenger.save()
                else:
                    passenger = Passenger(name=name, surname=surname, seats=seats, flight=flight)
                    passenger.save()

                return redirect('flight', flightId)
        else:
            addPassengerForm = AddPassengerToFlightForm(initial={"seats": 1}, seatsRemaining=seatsRemaining)

    return render(request, 'flightTable/flight.html', locals())


class SimpleTable(tables.Table):
    edit_entries = tables.TemplateColumn('<a href="/flight/{{record.id}}">Add passengers</a>')

    class Meta:
        model = Flight
        attrs = {'class': 'table'}

def simple_list(request):
    # populate()

    if "sort" in request.GET and request.GET.get("sort", "") != "edit_entries":
        queryset = Flight.objects.all().order_by(request.GET.get("sort", ""))
    else:
        queryset = Flight.objects.all()

    table = SimpleTable(queryset)
    table.paginate(page=request.GET.get('page', 1), per_page=25)
    return render(request, 'flightTable/flight_list.html', {'table': table})

def populate():
    airport1 = Airport(name="MIMUW")
    airport1.save()

    airport2 = Airport(name="PG")
    airport2.save()

    airport3 = Airport(name="MINIPW")
    airport3.save()

    airports=[airport1, airport2, airport3]

    for i in range(20):
        airline = Airline(name="airline nr"+i.__str__())
        airline.save()
        plane = Plane(airline=airline, registration_num="rn"+i.__str__(), seats=20+i%11)
        delta = datetime.timedelta(days=1, hours=i)
        today = datetime.datetime.now()
        date = datetime.datetime.now() + delta
        plane.save()
        for j in range(20):
            start = today+j*delta
            finnish = start+datetime.timedelta(hours=i%4+6, minutes=32*(j%10))
            flight = Flight(departure_airport=airports[j%3], arrival_airport=airports[(j+1)%3],
                            departure_time=start, arrival_time=finnish,
                            plane=plane)
            flight.save()

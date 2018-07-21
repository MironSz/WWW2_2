from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

from flightTable.forms import RegistrationForm,AddPassengerToFlightForm
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login as login_to_session
from django.contrib.auth.models import User
from .models import Flight, Passenger, Airport


def main(request):
    # articles = Article.objects.all()
    flights = Flight.objects.all()
    return render(request, 'flightTable/main.html', {
        'flights': flights,
    })


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
    passengers = fl.passenger.all()

    if request.user.is_authenticated:
        if request.method == 'POST':
            addPassengerForm = AddPassengerToFlightForm(request.POST)
            addPassengerForm.full_clean()
            if addPassengerForm.is_valid():
                passenger = addPassengerForm.save(commit=False)
                passenger.name = request.POST.get('name')
                passenger.surname = request.POST.get('surname')
                if Passenger.objects.filter(name = passenger.name,surname=passenger.surname).exists():
                    passenger = Passenger.objects.filter(name = passenger.name,surname=passenger.surname).first()
                else:
                    passenger.save()

                fl.passenger.add(passenger)



                return redirect('flight', flightId)
        else:
            addPassengerForm = AddPassengerToFlightForm()

    return render(request, 'flightTable/flight.html', locals())


class FlightList(ListView):
    model = Flight
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get a context
    #     context = super().get_context_data(**kwargs)
    #     # Add in a QuerySet of all the books
    #     context = super().get_context_data(**kwargs)
    #     context['departure_airport'] = Airport.objects.all()
    #     return context
    # context_object_name = 'my_favorite_publishers'


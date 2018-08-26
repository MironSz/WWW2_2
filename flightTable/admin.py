from django.contrib import admin
from .models import Airline, Plane, Airport, Passenger, Flight, Crew

admin.site.register(Airline)
admin.site.register(Plane)
admin.site.register(Airport)
admin.site.register(Passenger)
admin.site.register(Flight)
admin.site.register(Crew)


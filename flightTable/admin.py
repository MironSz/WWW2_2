from django.contrib import admin
from .models import Airline, Plane,Airport,Passenger,Flight

admin.site.register(Airline)
admin.site.register(Plane)
admin.site.register(Airport)
admin.site.register(Passenger)
admin.site.register(Flight)


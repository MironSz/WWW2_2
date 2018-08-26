from rest_framework import serializers
from flightTable.models import Crew
from django.contrib.auth.models import User


class CrewSerializers(serializers.ModelSerializer):
    # owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Crew
        fields = ('id', 'captain_name', 'captain_surname',)

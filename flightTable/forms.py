from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, Form, ValidationError
from .models import Passenger
import re

class AddPassengerToFlightForm(ModelForm):
    class Meta:
        model = Passenger
        fields = ['name', 'surname', "seats"]

    def __init__(self,*args,**kwargs):
        self.seatsRemaining = kwargs.pop("seatsRemaining")
        super(AddPassengerToFlightForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("seats") > self.seatsRemaining or cleaned_data.get("seats") < 1:
            msg = "There are not enough seats left."
            self.add_error("seats", msg)

        if re.search("[A-Z][a-z]+",cleaned_data.get("name")) is None \
                or re.search("[A-Z][a-z]+",cleaned_data.get("name")).group(0) != cleaned_data.get("name"):
            msg = "Weird name you have. Consider changing it."
            self.add_error("name", msg)

        if re.search("[A-Z][a-z]+",cleaned_data.get("surname")) is None \
                or re.search("[A-Z][a-z]+",cleaned_data.get("surname")).group(0) != cleaned_data.get("surname"):
            msg = "Weird surname you have. Consider changing it."
            self.add_error("surname", msg)

        return cleaned_data


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=64, label='Username')
    password = forms.CharField(max_length=64, label='Password', widget=forms.PasswordInput())

    def clean(self):
        super().clean()
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError('User with the same username already exists.')



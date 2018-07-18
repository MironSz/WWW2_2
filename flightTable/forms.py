from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, Form, ValidationError
from .models import Passenger


class AddPassengerToFlightForm(ModelForm):
    class Meta:
        model = Passenger
        fields = ['name', 'surname']

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=64, label='Username')
    password = forms.CharField(max_length=64, label='Password', widget=forms.PasswordInput())

    def clean(self):
        super().clean()
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError('User with the same username already exists.')



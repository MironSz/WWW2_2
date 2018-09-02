"""WWW2_2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth.views import LogoutView
import flightTable.views
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/', flightTable.views.simple_list),
    path('', flightTable.views.simple_list, name="main"),
    path('logout/', LogoutView.as_view(template_name='flightTable/logout.html'), name='logout'),
    path('login/', flightTable.views.login, name='login'),
    path('register/', flightTable.views.register, name='register'),
    re_path('flight/([0-9]+)/', flightTable.views.flight, name='flight'),
    path('api/flights_and_crews/', flightTable.views.get_crews, name='flights_and_crews'),
    path('api/change_crew/', flightTable.views.change_crew, name='update_crew'),
    path('api/login_REST/', flightTable.views.login_REST, name='login_REST'),

]
urlpatterns = format_suffix_patterns(urlpatterns)

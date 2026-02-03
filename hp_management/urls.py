from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"),
    path('appointment/', appointment, name='appointment'),
    path('my_appointment/', my_appointment, name="my_appointment"),
    path('edit_profile/', edit_profile, name="edit_profile"),
]

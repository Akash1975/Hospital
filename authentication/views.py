from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .forms import RegisterForm
from django.contrib import messages
from django.core.mail import send_mail
from .models import PasswordResetOTP
import random
from django.utils import timezone
# from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import User
import logging



# Create your views here.
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]

            user.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "auth/register.html", {"form": form})



def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")

    else:
        initial_data = {"username": "", "password": ""}
        form = AuthenticationForm(initial=initial_data)

    return render(request, "auth/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return render(request, "auth/login.html")

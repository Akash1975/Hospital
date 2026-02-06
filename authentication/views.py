from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from .forms import RegisterForm
from django.contrib import messages
from django.core.mail import send_mail
from .models import PasswordResetOTP
import random
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

from .forms import ForgotPasswordForm, OTPVerificationForm, ResetPasswordForm
from .models import PasswordResetOTP


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


# ================= SEND OTP =================
def forgot_password(request):

    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            try:
                user = User.objects.get(email=email)

                otp = str(random.randint(100000, 999999))

                PasswordResetOTP.objects.create(user=user, otp=otp)

                send_otp_email(email, otp)

                request.session["reset_user"] = user.id
                return redirect("verify_otp_reset")

            except User.DoesNotExist:
                messages.error(request, "Email not registered")

    else:
        form = ForgotPasswordForm()

    return render(request, "auth/forgot_password.html", {"form": form})


# ================= VERIFY OTP =================
def verify_otp_and_reset(request):

    if "reset_user" not in request.session:
        return redirect("forgot_password")

    user_id = request.session["reset_user"]

    if request.method == "POST":
        otp = request.POST.get("otp")
        new_pass = request.POST.get("new_password")
        confirm_pass = request.POST.get("confirm_password")

        otp_obj = PasswordResetOTP.objects.filter(user_id=user_id, otp=otp).last()

        if not otp_obj or otp_obj.is_expired():
            messages.error(request, "Invalid or expired OTP")
            return redirect("verify_otp")

        if new_pass != confirm_pass:
            messages.error(request, "Passwords do not match")
            return redirect("verify_otp")

        user = User.objects.get(id=user_id)
        user.set_password(new_pass)
        user.save()

        otp_obj.delete()
        del request.session["reset_user"]

        messages.success(request, "Password reset successfully")
        return redirect("login")

    return render(request, "auth/verify_otp_reset.html")


def send_otp_email(user_email, otp):

    subject = "Hospital Password Reset OTP"

    message = f"""
    Hello,

    Your OTP for password reset is:

    {otp}

    This OTP is valid for 5 minutes.

    If you did not request this, please ignore.

    Hospital Management System
    """

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )

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


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email not registered.")
            return redirect("forgot_password")

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)

        # Save or update OTP in DB
        otp_obj, created = PasswordResetOTP.objects.update_or_create(
            user=user, defaults={"otp": otp, "created_at": timezone.now()}
        )

        # Send OTP via email
        send_mail(
            "Your OTP for Password Reset",
            f"Hello user {user.username},\n\nYour OTP is: {otp}\nIt will expire in 10 minutes.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        # Store user id in session for verify_otp view
        request.session["reset_user_id"] = user.id

        # Show success message
        messages.success(request, f"OTP has been sent to {email}.")
        return redirect("verify_otp")

    return render(request, "auth/forgot_password.html")


def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        password = request.POST.get("password")

        user_id = request.session.get("reset_user_id")
        if not user_id:
            messages.error(request, "Session expired. Try again.")
            return redirect("forgot_password")

        user = User.objects.get(id=user_id)

        otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).first()

        if not otp_obj:
            messages.error(request, "Invalid OTP")
            return redirect("verify_otp")

        if otp_obj.is_expired():
            otp_obj.delete()
            messages.error(request, "OTP expired")
            return redirect("forgot_password")

        # ✅ Update password
        user.set_password(password)
        user.save()
        otp_obj.delete()

        # ✅ Send success email
        send_mail(
            "Password Changed Successfully",
            f"""Hello {user.first_name or user.username},

Your password has been changed successfully.

If you did not perform this action, please contact support immediately.

Regards,
Hospital Management System
""",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        # Clear session
        del request.session["reset_user_id"]

        messages.success(request, "Password reset successful. Please login.")
        return redirect("login")

    return render(request, "auth/verify_otp.html")


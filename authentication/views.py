from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
import random

from .forms import (
    RegisterForm,
    ForgotPasswordForm,
    OTPVerificationForm,
    ResetPasswordForm,
)
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

                # Add better error handling
                try:
                    send_otp_email(user, otp)
                    request.session["reset_user"] = user.id
                    messages.success(request, "OTP sent to your email")
                    return redirect("verify_otp_reset")
                except ValueError as ve:
                    messages.error(
                        request,
                        "Email service is not configured. Please contact administrator.",
                    )
                    print(f"Email configuration error: {ve}")
                except Exception as e:
                    messages.error(request, f"Failed to send email. Please try again.")
                    print(f"Email sending failed: {e}")

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
            return redirect("verify_otp_reset")

        if new_pass != confirm_pass:
            messages.error(request, "Passwords do not match")
            return redirect("verify_otp_reset")

        user = User.objects.get(id=user_id)
        user.set_password(new_pass)
        user.save()
        send_password_changed_email(user)

        otp_obj.delete()
        del request.session["reset_user"]

        messages.success(request, "Password reset successfully")
        return redirect("login")

    return render(request, "auth/verify_otp_reset.html")


def send_otp_email(user, otp):
    from django.conf import settings
    from django.core.mail import send_mail
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

    subject = "Hospital Password Reset OTP"

    message = f"""
Hello user {user.username},

We received a request to reset your password.

Your OTP for password reset is:

{otp}

This OTP is valid for 10 minutes.

If you did not request this, please ignore this email.

Hospital Management System
"""

    try:
        validate_email(user.email)

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

    except ValidationError:
        raise ValueError("Invalid email address format.")


def send_password_changed_email(user):
    from django.conf import settings
    from django.core.mail import send_mail

    subject = "Password Changed Successfully"

    message = f"""
Hello user {user.username},

Your password has been successfully changed.

If you did not perform this action, please contact support immediately.

Thank you,
Hospital Management System
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def resend_otp(request):
    if "reset_user" not in request.session:
        return redirect("forgot_password")

    user_id = request.session["reset_user"]

    try:
        user = User.objects.get(id=user_id)

        # Delete old OTPs (optional but recommended)
        PasswordResetOTP.objects.filter(user=user).delete()

        # Generate new OTP
        otp = str(random.randint(100000, 999999))
        PasswordResetOTP.objects.create(user=user, otp=otp)

        # Send new OTP
        send_otp_email(user, otp)

        messages.success(request, "New OTP sent successfully.")

    except Exception as e:
        messages.error(request, "Failed to resend OTP.")
        print("Resend OTP error:", e)

    return redirect("verify_otp_reset")

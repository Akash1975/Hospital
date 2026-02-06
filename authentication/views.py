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


def send_otp(request):
    """
    General endpoint to send OTP for various purposes
    Expects POST request with 'email' and 'purpose' parameters
    """
    if request.method == "POST":
        email = request.POST.get("email")
        purpose = request.POST.get("purpose", "verification")
        user_email = request.POST.get("user_email")  # Email of the user making the request (for security)
        
        if not email:
            messages.error(request, "Email is required.")
            return redirect("home")  # or wherever appropriate
        
        # In a real app, you'd validate the user has permission to send OTP to this email
        # For now, we'll assume the user is authenticated and can send to any email
        user = None
        if purpose in ['password_reset', 'verification', 'account_activation']:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                if purpose == "password_reset":
                    messages.error(request, "Email not registered.")
                    return redirect("forgot_password")
                # For other purposes, we might not require user to exist
        
        otp_sent, otp = send_general_otp(request, email, purpose, user)
        
        if otp_sent:
            messages.success(request, f"OTP has been sent to {email}.")
            
            # Store OTP purpose in session if needed
            if purpose == "password_reset":
                request.session["reset_user_id"] = user.id
                return redirect("verify_otp")
        else:
            messages.error(request, "Failed to send OTP. Please try again.")
    
    # Redirect back to appropriate page based on purpose
    if request.META.get('HTTP_REFERER'):
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect("home")


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
        otp_message = f"Hello {user.first_name or user.username},\n\nYour OTP is: {otp}\nIt will expire in 10 minutes."
        
        otp_sent = send_otp_email(
            user=user,
            email=email,
            otp=otp,
            subject="Your OTP for Password Reset",
            message_body=otp_message,
        )
        
        if not otp_sent:
            messages.error(request, "Failed to send OTP. Please try again.")
            return redirect("forgot_password")

        # Store user id in session for verify_otp view
        request.session["reset_user_id"] = user.id

        # Show success message
        messages.success(request, f"OTP has been sent to {email}.")
        return redirect("verify_otp")

    return render(request, "auth/forgot_password.html")


def send_otp_email(user, email, otp, subject="Your OTP for Verification", message_body="Hello user,\n\nYour OTP is: {otp}\nIt will expire in 10 minutes."):
    """
    Utility function to send OTP via email
    Works both in development and production (Render deployment)
    """
    try:
        # Check if email settings are properly configured
        if not hasattr(settings, 'EMAIL_HOST') or not settings.EMAIL_HOST:
            print("Email settings are not configured properly")
            return False
            
        send_mail(
            subject,
            message_body,
            settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        print(f"OTP sent successfully to {email}")  # For debugging purposes
        return True
    except Exception as e:
        print(f"Error sending OTP: {str(e)}")  # Log error for debugging
        logging.error(f"Error sending OTP: {str(e)}")
        return False

def send_general_otp(request, email, purpose="verification", user=None):
    """
    General function to send OTP for different purposes
    Purpose can be 'verification', 'password_reset', 'account_activation', etc.
    """
    # Generate a 6-digit OTP
    otp = random.randint(100000, 999999)
    
    if purpose == "password_reset" and user:
        # Handle password reset OTP
        otp_obj, created = PasswordResetOTP.objects.update_or_create(
            user=user, defaults={"otp": str(otp), "created_at": timezone.now()}
        )
        subject = "Your OTP for Password Reset"
        message_body = f"Hello {user.username},\n\nYour OTP for password reset is: {otp}\nIt will expire in 10 minutes."
    elif purpose == "verification" and user:
        # For account verification
        subject = "Your Account Verification OTP"
        message_body = f"Hello {user.first_name or user.username},\n\nYour account verification OTP is: {otp}\nIt will expire in 10 minutes."
    elif purpose == "account_activation" and user:
        # For account activation
        subject = "Your Account Activation OTP"
        message_body = f"Hello {user.first_name or user.username},\n\nYour account activation OTP is: {otp}\nIt will expire in 10 minutes."
    else:
        # Generic OTP
        subject = "Your OTP for Verification"
        message_body = f"Hello,\n\nYour OTP is: {otp}\nIt will expire in 10 minutes."
    
    # Send OTP
    otp_sent = send_otp_email(
        user=user,
        email=email,
        otp=otp,
        subject=subject,
        message_body=message_body
    )
    
    return otp_sent, otp

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
        send_otp_email(
            user=user,
            email=user.email,
            otp="",
            subject="Password Changed Successfully",
            message_body=f"""Hello {user.first_name or user.username},

Your password has been changed successfully.

If you did not perform this action, please contact support immediately.

Regards,
Hospital Management System
""",
        )

        # Clear session
        del request.session["reset_user_id"]

        messages.success(request, "Password reset successful. Please login.")
        return redirect("login")

    return render(request, "auth/verify_otp.html")


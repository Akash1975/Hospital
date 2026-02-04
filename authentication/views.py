from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from .forms import RegisterForm
from .models import PasswordResetOTP
import random
from django.core.mail import send_mail

# ================= EMAIL FUNCTION =================
from django.core.mail import EmailMessage
from django.conf import settings

def send_email(subject, message, to_email):
    """
    Sends an email via Gmail SMTP configured in settings.py.
    Works for production servers like Render.
    """
    try:
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )
        email.content_subtype = "plain"  # keep simple for Gmail
        email.send(fail_silently=False)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")


# ================= REGISTER VIEW =================
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


# ================= LOGIN VIEW =================
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "auth/login.html", {"form": form})


# ================= LOGOUT VIEW =================
def logout_view(request):
    logout(request)
    return redirect("login")


# ================= FORGOT PASSWORD =================
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email not registered.")
            return redirect("forgot_password")

        # Generate OTP
        otp = random.randint(100000, 999999)

        # Save OTP
        PasswordResetOTP.objects.update_or_create(
            user=user,
            defaults={"otp": otp, "created_at": timezone.now()}
        )

        # Send OTP email
        send_email(
            "Your OTP for Password Reset",
            f"""Hello {user.username},

Your OTP for password reset is: {otp}

This OTP will expire in 10 minutes.

Regards,
Hospital Management System
""",
            user.email,
        )

        # Save user id in session
        request.session["reset_user_id"] = user.id
        messages.success(request, "OTP has been sent to your email.")
        return redirect("verify_otp")

    return render(request, "auth/forgot_password.html")


# ================= VERIFY OTP & RESET PASSWORD =================
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
            messages.error(request, "Invalid OTP.")
            return redirect("verify_otp")

        if otp_obj.is_expired():
            otp_obj.delete()
            messages.error(request, "OTP expired.")
            return redirect("forgot_password")

        # Set new password
        user.set_password(password)
        user.save()
        otp_obj.delete()

        # Send success email
        send_email(
            "Password Changed Successfully",
            f"""Hello {user.first_name or user.username},

Your password has been changed successfully. 
If you did not perform this action, please contact support immediately.

Regards,
Hospital Management System
""",
            user.email,
        )

        # Clear session
        del request.session["reset_user_id"]
        messages.success(request, "Password reset successful. Please login.")
        return redirect("login")

    return render(request, "auth/verify_otp.html")

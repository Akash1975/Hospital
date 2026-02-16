from django.urls import path
from .views import *


urlpatterns = [
    path("login/", login_view, name="login"),
    path("", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("forgot-password/", forgot_password, name="forgot_password"),
    path("verify-reset/", verify_otp_and_reset, name="verify_otp_reset"),
    path("resend-otp/", resend_otp, name="resend_otp"),

]

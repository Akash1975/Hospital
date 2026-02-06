"""
Test script to verify OTP functionality
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')

# Setup Django
django.setup()

from django.test import RequestFactory
from authentication.views import send_otp_email, send_general_otp
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages import get_messages
import random


def create_test_request():
    """Helper function to create a test request with session support"""
    factory = RequestFactory()
    request = factory.post('/send-otp/')
    
    # Add session to request
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    
    return request


def test_send_otp_functionality():
    """Test the OTP sending functionality"""
    print("Testing OTP functionality...")
    
    # Create a test user
    test_user, created = User.objects.get_or_create(
        username='testuser',
        email='test@example.com',
        defaults={'first_name': 'Test', 'last_name': 'User'}
    )
    
    request = create_test_request()
    
    # Test the send_otp_email function
    otp = random.randint(100000, 999999)
    print(f"Generated OTP: {otp}")
    
    try:
        result = send_otp_email(
            user=test_user,
            email='test@example.com',
            otp=otp,
            subject="Test OTP",
            message_body=f"Hello, your test OTP is: {otp}"
        )
        
        print(f"send_otp_email result: {result}")
        
        if result:
            print("✅ OTP email sent successfully!")
        else:
            print("❌ Failed to send OTP email")
            
    except Exception as e:
        print(f"❌ Error in send_otp_email: {str(e)}")
    
    # Test the send_general_otp function
    try:
        otp_sent, otp_value = send_general_otp(
            request=request,
            email='test@example.com',
            purpose='verification',
            user=test_user
        )
        
        print(f"send_general_otp result: {otp_sent}, OTP: {otp_value}")
        
        if otp_sent:
            print("✅ General OTP sent successfully!")
        else:
            print("❌ Failed to send general OTP")
            
    except Exception as e:
        print(f"❌ Error in send_general_otp: {str(e)}")


if __name__ == "__main__":
    test_send_otp_functionality()
"""
Test script to verify normal email functionality (Gmail SMTP)
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

from django.core.mail import send_mail
from django.contrib.auth.models import User
import os


def test_normal_email():
    """Test sending email using normal Gmail SMTP configuration"""
    print("Testing normal email functionality (Gmail SMTP)...")
    
    # Create a test user
    test_user, created = User.objects.get_or_create(
        username='testuser',
        email='test@example.com',
        defaults={'first_name': 'Test', 'last_name': 'User'}
    )
    
    try:
        # Test sending a simple email
        result = send_mail(
            subject="Test Email - Normal SMTP",
            message="This is a test email using normal Gmail SMTP configuration.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],  # Use a real email for actual testing
            fail_silently=False,
        )
        
        print(f"Email send result: {result}")
        
        if result:
            print("✅ Normal email sent successfully!")
            print("Configuration in use:")
            print(f"  EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Not set')}")
            print(f"  EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
            print(f"  EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
            print(f"  EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
            print(f"  EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
            print(f"  DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
        else:
            print("❌ Failed to send email")
            
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        print("This could be due to incorrect email configuration or network issues.")


if __name__ == "__main__":
    test_normal_email()
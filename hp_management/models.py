from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    doctor_image = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return f"Dr. {self.name} ({self.specialization})"


class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    date = models.DateField()
    time = models.TimeField()

    address = models.TextField(max_length=100, blank=True, null=True)

    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)

    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
    ]
    appointment_status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="PENDING"
    )
    

class About(models.Model):
    about_image = CloudinaryField('image', blank=True, null=True)
    about_text = models.TextField()
    
    def __str__(self):
        return self .about_text


class Services(models.Model):
    service_name = models.CharField(max_length=100)
    service_description = models.TextField()

    def __str__(self):
        return self.service_name
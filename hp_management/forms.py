from django import forms
from django.contrib.auth.models import User
from .models import Profile, Appointment, Doctor

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_image']
        
# class RegisterForm(forms.ModelForm):
#     password1 = forms.CharField(widget=forms.PasswordInput)
#     password2 = forms.CharField(widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'email']

#     def clean_email(self):
#         email = self.cleaned_data.get("email")
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError("Email already registered")
#         return email

#     def clean(self):
#         cleaned_data = super().clean()
#         if cleaned_data.get("password1") != cleaned_data.get("password2"):
#             raise forms.ValidationError("Passwords do not match")

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password1"])
#         if commit:
#             user.save()
#         return user



class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'doctor',
            'name',
            'email',
            'phone',
            'date',
            'time',
            'address',
            'message'
        ]
        
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }
        
        

    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(is_active=True),
        empty_label="Select Doctor"
    )
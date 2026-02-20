from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import EditProfileForm, ProfileImageForm, AppointmentForm
from django.contrib.auth.models import User
from .models import Profile, Appointment, Doctor, About, Services
from django.contrib import messages

# Create your views here.


@login_required(login_url="login")
def home(request):
    about_doctors = Doctor.objects.filter(is_active=True)
    about = About.objects.first()
    services = Services.objects.all()
    return render(request, "hospital/home.html", {
        "about_doctors": about_doctors,
        "about": about,
        "services": services
    })

@login_required(login_url="login")
def my_appointment(request):
    appointments = Appointment.objects.filter(user=request.user).order_by('-created_at')
    return render(
        request,
        "hospital/my_appointment.html",
        {"appointments": appointments}
    )


@login_required(login_url="login")
def edit_profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        user_form = EditProfileForm(request.POST, instance=user)
        profile_form = ProfileImageForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("edit_profile")
    else:
        user_form = EditProfileForm(instance=user)
        profile_form = ProfileImageForm(instance=profile)

    return render(
        request,
        "hospital/edit_profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
        },
    )


# from django.shortcuts import render

# def edit_profile(request):
#     return render(request, 'hospital/edit_profile.html')


@login_required(login_url='login')
def appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            messages.success(request, "Appointment booked successfully!")
            return redirect('home') 
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = AppointmentForm()
    
    return render(request, 'hospital/appointment.html', {'form': form})


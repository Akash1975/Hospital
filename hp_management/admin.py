from django.contrib import admin
from .models import Appointment, Doctor, About, Services

@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('service_name',)

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('about_text',)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'phone', 'email', 'is_active')
    list_filter = ('specialization', 'is_active')
    search_fields = ('name', 'specialization')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'email', 'phone', 'date', 'time','doctor',
        'created_at', 'user', 'message', 'appointment_status'
    )
    list_filter = ('date', 'appointment_status')  # allow filtering by status
    search_fields = ('name', 'email', 'phone')
    ordering = ('-created_at',)

    # Make all fields read-only except appointment_status
    readonly_fields = (
        'user', 'name', 'email', 'phone','doctor',
        'date', 'time', 'message','address', 'created_at'
    )

    # Allow editing only appointment_status
    fields = readonly_fields + ('appointment_status',)
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

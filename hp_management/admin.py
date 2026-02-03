from django.contrib import admin
from .models import Appointment, Doctor, About, Services


@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('service_name',)

@admin.register(About)
class aboutAdmin(admin.ModelAdmin):
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
        'created_at', 'user', 'message'
    )
    list_filter = ('date',)
    search_fields = ('name', 'email', 'phone')
    ordering = ('-created_at',)


    readonly_fields = (
        'user', 'name', 'email', 'phone','doctor',
        'date', 'time', 'message','address', 'created_at','appointment_status'
    )


    def has_add_permission(self, request):
        return False


    def has_delete_permission(self, request, obj=None):
        return True

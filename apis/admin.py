from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Employee

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'phone_number')}),  
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'phone_number')}),
    )

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone','hourly_rate','status', 'role', 'date_joined')  
    search_fields = ['first_name', 'last_name', 'email']
    list_filter = ['role']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Employee, EmployeeAdmin)

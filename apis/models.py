from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('HR', 'HR'),
        ('Manager', 'Manager'),
        ('Software Engineer', 'Software Engineer'),
        ('Developer', 'Developer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Developer')
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.username


class Employee(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(
        max_length=50, 
        choices=[
            ('Software Engineer', 'Software Engineer'),
            ('Manager', 'Manager'),
            ('HR', 'HR'),
            ('Developer', 'Developer'),
        ], 
        default='Developer', 
        null=True, 
        blank=True
    )
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(
        max_length=50, 
        choices=[
            ('Active', 'Active'),
            ('Inactive', 'Inactive'),
        ], 
        default='Active', 
        null=True, 
        blank=True
    )
    date_joined = models.DateField(null=True, blank=True)
    custom_user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='employee', 
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Payroll(models.Model):
    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_working_days = models.IntegerField(null=True, blank=True)
    days_worked = models.IntegerField(null=True, blank=True)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payroll for {self.employee} on {self.payment_date}"
    

class LeaveRequest(models.Model):
    LEAVE_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=50, choices=[
        ('Sick Leave', 'Sick Leave'),
        ('Casual Leave', 'Casual Leave'),
        ('paid Leave', 'paid Leave'),
    ])
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=LEAVE_STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rejection_reason = models.TextField(null=True, blank=True)  # Add this line

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} ({self.status})"

    
class ScheduledPayment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed')],
        default='Scheduled'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - {self.amount} on {self.payment_date}"

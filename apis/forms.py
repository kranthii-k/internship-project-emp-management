import math
from django.contrib.auth.forms import UserCreationForm
from jsonschema import ValidationError # type: ignore
from apis.models import CustomUser  
from django import forms
from .models import Employee, Payroll, ScheduledPayment
from .models import LeaveRequest
from django.utils.timezone import now


class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'phone', 'role','hourly_rate','status', 'date_joined']  

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['employee', 'total_working_days', 'days_worked', 'monthly_salary']

    def __init__(self, *args, **kwargs):
        super(PayrollForm, self).__init__(*args, **kwargs)
        self.fields['employee'].widget.attrs.update({'class': 'form-control'})

class PaymentForm(forms.ModelForm):
    class Meta:
        model = ScheduledPayment
        fields = ['employee', 'amount', 'payment_date']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }

class SchedulePayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['employee', 'total_working_days', 'days_worked', 'monthly_salary', 'payment_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].empty_label = "Select an Employee"

    
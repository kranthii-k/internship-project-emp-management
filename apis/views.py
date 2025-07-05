import json
from urllib import request
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from apis.forms import CustomUserCreationForm, SchedulePayrollForm  
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from .models import Employee, Payroll, ScheduledPayment
from .serializers import EmployeeSerializer
from datetime import datetime,date, timezone
from django.contrib import messages
from apis.models import LeaveRequest
from apis.forms import LeaveRequestForm, PayrollForm
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from apis.utils import send_email_notification, send_html_email_notification
from apis.models import CustomUser
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.core.mail import send_mail




class EmployeeCreateView(generics.CreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

def home(request):
    employees = Employee.objects.all()
    return render(request, 'home.html', {'employees': employees})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.role = form.cleaned_data['role'] 
            user.save()
            login(request, user)  
            messages.success(request, "Registration successful.")
            print(user)
            return redirect('home')  

        else:
            messages.error(request, "Error in registration. Please try again.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'login/register.html', {'form': form})
@login_required
def add_employee(request):
    if request.user.role in ['HR', 'Manager']: 
        if request.method == "POST":

            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            role = request.POST.get('role')  
            hourly_rate = request.POST.get('hourly_rate')

            if first_name and last_name and email and role and hourly_rate :
                user = CustomUser(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    role=role,
                    hourly_rate=hourly_rate,
                )
                user.save()

                messages.success(request, "Employee added successfully.")
                return redirect('home')  
            else:
                messages.error(request, "Please fill in all fields.")
                
        return render(request, 'Admin/add_employee.html')  
    else:
        return redirect('home') 

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            if user.role == 'HR' or user.role == 'Manager':
                return redirect('home')  
            else:
                return redirect('home')  
        else:
            messages.error(request, 'Invalid credentials')
            return render(request, 'login/login.html')
    
    return render(request, 'login/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def employee_list(request):
    users = CustomUser.objects.all().order_by('id')
    return render(request, 'Admin/employee_list.html', {'users': users})

@login_required
def employee_detail(request, employee_id):
    employee = get_object_or_404(CustomUser, id=employee_id)
    employees = Employee.objects.filter(role__in=['Developer', 'Software Engineer'])
    return render(request, 'Admin/employee_profile.html', {'employee': employee, 'employees': employees})


@login_required
def employee_edit(request, employee_id):
    employee = get_object_or_404(CustomUser, id=employee_id)
    if request.method == 'POST':
        employee.first_name = request.POST.get('first_name')
        employee.last_name = request.POST.get('last_name')
        employee.email = request.POST.get('email')
        employee.phone = request.POST.get('phone')
        employee.role = request.POST.get('role')
        employee.status = request.POST.get('status')
        employee.hourly_rate = request.POST.get('hourly_rate')
        date_joined = request.POST.get('date_joined')
        employee.date_joined = date_joined if date_joined else datetime.now().date()
        employee.save()
        return redirect('home')
    return render(request, 'Admin/employee_edit.html', {'employee': employee})

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user  
        user.first_name = request.POST.get('firstname')  
        user.last_name = request.POST.get('lastname')    
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        
        if not user.first_name or not user.last_name or not user.email or not user.phone:
            from django.contrib import messages
            messages.error(request, "All fields are required!")
            return render(request, 'Admin/employee_profile.html', {'user': user})
        
        user.save()  
        return redirect('employee_profile') 
    return render(request, 'Admin/employee_profile.html', {'user': request.user})

def delete_employee(request, employee_id):
    try:
        employee = get_object_or_404(CustomUser, id=employee_id)
        employee.delete() 
        messages.success(request, "Employee deleted successfully.")
    except Employee.DoesNotExist:
        messages.error(request, "The employee you are trying to delete does not exist.")
    return redirect('employee_list') 

def generate_payroll(request):
    return redirect("payroll/generate_payroll.html")


@login_required
def leave_requests(request):
    leave_requests = LeaveRequest.objects.all()  
    return render(request, 'leave/leave_requests.html', {'leave_requests': leave_requests})
@login_required
def create_leave_request(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = request.user  
            leave_request.status = 'Pending' 
            leave_request.save()
            return redirect('leave_list')
    else:
        form = LeaveRequestForm()

    return render(request, 'leave/leave_request_form.html', {'form': form})

def send_email_notification(subject, message, recipient_email, html_message=None):
    email = EmailMultiAlternatives(subject, message, to=[recipient_email])
    if html_message:
        email.attach_alternative(html_message, "text/html")
    email.send()

@login_required
def check_leave(request, employee_id):
    print(employee_id)
    user = get_object_or_404(CustomUser, id=employee_id)
    print(user)
    try:
        employee = CustomUser.objects.get(username=user)
        print(employee)
    except Employee.DoesNotExist:
        raise Http404("Employee not found.")

    today = timezone.now().date()  
    date_of_joined = employee.date_joined.date() 
    
    total_days_with_company = (today - date_of_joined).days 

    total_leave_taken = 0
    leave_requests = LeaveRequest.objects.filter(employee=employee, status="Approved")
    for leave_request in leave_requests:
        total_leave_taken += (leave_request.end_date - leave_request.start_date).days + 1 

    annual_leave_quota = 20 
    remaining_leave = annual_leave_quota - total_leave_taken

    return render(request, 'emails/check_leave_info.html', {
        'employee': employee,
        'leave_requests': leave_requests,
        'total_days_with_company': total_days_with_company,
        'total_leave_taken': total_leave_taken,
        'remaining_leave': remaining_leave,
    })

@login_required
def approve_leave_request(request, leave_request_id):
    leave_request = LeaveRequest.objects.get(id=leave_request_id)
    leave_request.status = 'Approved'
    leave_request.save()

    subject = "Leave Request Approved"
    context = {
        'employee_name': leave_request.employee.first_name,
        'start_date': leave_request.start_date,
        'end_date': leave_request.end_date,
        'users': [leave_request.employee]  # Pass the user in a list for template compatibility
    }
    email_html_message = render_to_string('emails/leave_notification.html', context)
    email_plain_message = strip_tags(email_html_message)

    recipient_email = leave_request.employee.email
    send_email_notification(subject, email_plain_message, recipient_email, html_message=email_html_message)

    return redirect('leave_requests')

@login_required
def reject_leave_request(request, leave_request_id):
    leave_request = LeaveRequest.objects.get(id=leave_request_id)
    leave_request.status = 'Rejected'
    leave_request.save()

    subject = "Leave Request Rejected"
    context = {
        'employee_name': leave_request.employee.first_name,
        'start_date': leave_request.start_date,
        'end_date': leave_request.end_date,
    }
    email_html_message = render_to_string('emails/leave_rejection_notification.html', context)
    email_plain_message = strip_tags(email_html_message)

    recipient_email = leave_request.employee.email
    send_email_notification(subject, email_plain_message, recipient_email, html_message=email_html_message)

    return redirect('leave_requests')


@login_required
def leave_list(request):
    leave_requests = LeaveRequest.objects.filter(employee=request.user)
    return render(request, 'leave/leave_list.html', {'leave_requests': leave_requests})

@login_required
def update_leave_request(request, leave_request_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)
    
    if request.user != leave_request.employee:
        return HttpResponseForbidden("You cannot edit this leave request.")

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, instance=leave_request)
        if form.is_valid():
            form.save()
            return redirect('leave_list') 
    else:
        form = LeaveRequestForm(instance=leave_request)

    return render(request, 'leave/update_leave_request.html', {'form': form, 'leave_request': leave_request})

@login_required
def delete_leave_request(request, leave_request_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)
    
    if request.user != leave_request.employee:
        return HttpResponseForbidden("You cannot delete this leave request.")

    leave_request.delete()  
    return redirect('leave_list') 

@login_required
def review_leave_requests(request, leave_request_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)

    if request.user.role in ['HR', 'Manager']:
        leave_request = LeaveRequest.objects.get(id=leave_request_id)
        if request.method == 'POST':
            status = request.POST.get('status')
            if status in ['Approved', 'Rejected']:
                leave_request.status = status
                leave_request.save()
                return redirect('home')  
        return render(request, 'leave/review_leave_request.html', {'leave_request': leave_request})
    else:
        return redirect('home')  
    

@login_required
def payroll_list(request):
    if request.user.is_authenticated:
        payrolls = Payroll.objects.filter(employee=request.user.employee)  
    else:
        payrolls = Payroll.objects.all()  

    return render(request, 'Admin/payment_list.html', {'payments': payrolls})


@login_required
def schedule_payroll(request):
    users = CustomUser.objects.all() 
    
    employees_data = [
        {
            'id': user.id,
            'username': user.username,
            'hourly_rate': float(user.hourly_rate) if user.hourly_rate else None,  
            'date_joined': user.date_joined.isoformat() if user.date_joined else None, 
        }
        for user in users
    ]
    
    employees_data_json = json.dumps(employees_data)  

    return render(request, 'payroll/schedule_payroll.html', {'employees_data': employees_data_json, 'users': users})


@login_required
def schedule_payment_hr(request):
    if request.method == "POST":
        form = PayrollForm(request.POST)
        if form.is_valid():
            payroll = form.save(commit=False)
            payroll.employee = request.user.employee
            payroll.total_working_days = payroll.days_worked
            payroll.days_worked = payroll.days_worked
            payroll.monthly_salary = payroll.employee.hourly_rate * 160
            payroll.payment_date = form.cleaned_data['payment_date']
            payroll.save()
            return redirect('manage_payroll_hr')  
    else:
        form = PayrollForm()
    return render(request, 'payroll/schedule_payment.html', {'form': form})

@login_required
def view_payroll_employee(request):
    payrolls = Payroll.objects.filter(employee=request.user.id)
    return render(request, 'payroll/view_payroll.html', {'payrolls': payrolls})


@login_required
def manage_payroll_hr(request):
    if request.method == "POST":
        form = SchedulePayrollForm(request.POST)
        if form.is_valid():
            payroll = form.save(commit=False)
            payroll.save()

            try:
                employee_email = payroll.employee.email
                print("Employee Email: ", employee_email)

                subject = "Payroll Scheduled Successfully"
                context = {
                    'username': payroll.employee.username,
                    'total_working_days': payroll.total_working_days,
                    'days_worked': payroll.days_worked,
                    'monthly_salary': payroll.monthly_salary,
                }

                email_html_message = render_to_string('emails/payroll_notification.html', context)

                send_email_notification(subject, "", employee_email, html_message=email_html_message)
                print("Email sent successfully")
                messages.success(request, "Payroll scheduled and email notification sent successfully.")
            except Exception as e:
                print(f"Error while sending email: {e}")
                messages.error(request, f"Payroll scheduled, but email could not be sent. Error: {str(e)}")

            return redirect('manage_payroll_hr')
        else:
            payrolls = Payroll.objects.all()
            return render(request, 'payroll/manage_payroll.html', {'payrolls': payrolls, 'form_errors': form.errors})

    payrolls = Payroll.objects.all()
    return render(request, 'payroll/manage_payroll.html', {'payrolls': payrolls})

@login_required
def get_employee_details(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
        
        date_joined = employee.date_joined
        today = datetime.date.today()
        total_working_days = (today - date_joined).days

        days_worked = min(total_working_days, 20)

        data = {
            "days_worked": days_worked,
            "total_working_days": total_working_days,
            "monthly_salary": days_worked * (employee.salary / total_working_days),  
        }
        return JsonResponse(data)
    except Employee.DoesNotExist:
        return JsonResponse({"error": "Employee not found"}, status=404)
    
@login_required
def delete_payroll(request, payroll_id):
    try:
        payroll = Payroll.objects.get(id=payroll_id)
        payroll.delete()
        return redirect('manage_payroll_hr')
    except Payroll.DoesNotExist:
        return redirect('manage_payroll_hr')
    
@login_required
def edit_payroll(request, payroll_id):
    try:
        payroll = Payroll.objects.get(id=payroll_id)
        if request.method == "POST":
            form = PayrollForm(request.POST, instance=payroll)
            if form.is_valid():
                form.save()
                return redirect('manage_payroll_hr')
        else:
            form = PayrollForm(instance=payroll)
        return render(request, 'payroll/edit_payroll.html', {'form': form})
    except Payroll.DoesNotExist:
        return redirect('manage_payroll_hr')
    
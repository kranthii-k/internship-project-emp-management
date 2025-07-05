from django.urls import path # type: ignore
from apis import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('logout/', views.user_logout, name='user_logout'),  
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),

    path('add_employee/', views.add_employee, name='add_employee'),
    path('employee_list/', views.employee_list, name='employee_list'),
    path('employee_detail/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('profile/<int:employee_id>', views.employee_detail, name='employee_profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('edit_employee/<int:employee_id>/', views.employee_edit, name='employee_edit'),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('delete_employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),

    
    path('approve-leave-request/<int:leave_request_id>/', views.approve_leave_request, name='approve_leave_request'),
    path('reject-leave-request/<int:leave_request_id>/', views.reject_leave_request, name='reject_leave_request'),
    path('check-leave/<int:employee_id>/', views.check_leave, name='check_leave'),
    path('leave-request/update/<int:leave_request_id>/', views.update_leave_request, name='update_leave_request'),
    path('leave-request/delete/<int:leave_request_id>/', views.delete_leave_request, name='delete_leave_request'),
    path('leave-requests/', views.leave_requests, name='leave_requests'),
    path('leave_list/', views.leave_list, name='leave_list'),
    path('review_leave_request/<int:leave_request_id>/', views.review_leave_requests, name='review_leave_requests'),
    path('create_leave_request/', views.create_leave_request, name='create_leave_request'),
    path('generate_payroll/', views.generate_payroll, name='generate_payroll'),

    path('schedule-payroll/', views.schedule_payroll, name='schedule_payroll'),
    path('payment_list/', views.payroll_list, name='payment_list'),
    path('schedule_payment_hr/', views.schedule_payment_hr, name='schedule_payment_hr'),
    path('view_payroll_employee/', views.view_payroll_employee, name='view_payroll_employee'),
    path('manage_payroll_hr/', views.manage_payroll_hr, name='manage_payroll_hr'),
    path("api/employee/<int:employee_id>/", views.get_employee_details, name="get_employee_details"),
    path('edit_payroll/<int:payroll_id>/', views.edit_payroll, name='edit_payroll'),
    path('delete_payroll/<int:payroll_id>/', views.delete_payroll, name='delete_payroll'),

    
    path('', views.home, name='home'),
]

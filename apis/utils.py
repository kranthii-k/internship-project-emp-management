from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from datetime import date

def send_email_notification(subject, message, recipient_email, html_message=None):
    send_mail(
        subject=subject,
        message=message,  # Fallback plain text message
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[recipient_email],
        fail_silently=False,
        html_message=html_message  # Add this for HTML content
    )

def send_html_email_notification(subject, message, recipient_email):
    context = {'subject': subject, 'message': message}
    html_message = render_to_string('emails/leave_notification.html', context)
    email = EmailMessage(subject, html_message, settings.EMAIL_HOST_USER, [recipient_email])
    email.content_subtype = 'html'
    email.send()

def check_leave(employee):
    today = date.today()
    days_with_company = (today - employee.date_joined).days
    leave_taken = employee.leave_taken  
    remaining_leave = employee.total_leave - leave_taken 

    return {
        'total_days_with_company': days_with_company,
        'total_leave_taken': leave_taken,
        'remaining_leave': remaining_leave,
    }

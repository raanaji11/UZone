from django.core.mail import send_mail
from UZone import settings

def send_email(email):
    subject = " UZone order"
    message = " your order has been palced successfully..Thankyou."
    send_mail(subject, message, from_email=settings.EMAIL_HOST_USER, recipient_list=[email])
    return "Done"

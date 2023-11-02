# django
from django.core.mail import send_mail

from celery import shared_task
import environ


env = environ.Env()


@shared_task(name="Send Email Task")
def send_email_task(subject,
                    message,
                    recipient_list,
                    from_email=env("DEFAULT_FROM_EMAIL"),
                    **kwargs):
    send_mail(subject, message, from_email, recipient_list, **kwargs)

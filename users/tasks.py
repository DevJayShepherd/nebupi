'''
Ready SaaS Source Code

Copyright 2023 Ready SaaS

Licensed under Ready SaaS Proprietary License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.readysaas.app/licenses/

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


# django
from django.core.mail import send_mail

from celery import shared_task
import os
import environ


# Setup environment variables with fallback to .env file
env = environ.Env()


@shared_task(name="Send Email Task")
def send_email_task(subject,
                    message,
                    recipient_list,
                    from_email='{} <{}>'.format(
                        os.getenv("DEFAULT_FROM_NAME", env("DEFAULT_FROM_NAME")),
                        os.getenv("DEFAULT_FROM_EMAIL", env("DEFAULT_FROM_EMAIL"))
                    ),
                    **kwargs):
    send_mail(subject, message, from_email, recipient_list, **kwargs)

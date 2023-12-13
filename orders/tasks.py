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


# orders
from .models import Subscription, SubscriptionStatus

# users
from users.tasks import send_email_task

from celery import shared_task
import datetime


@shared_task(name="Monitor Subscriptions")
def monitor_subscriptions_task():
    # iterate over all subscriptions
    # if today is the end date, set status to inactive
    # if today is the end date, send email to user
    for subscription in Subscription.objects.filter(status=SubscriptionStatus.ACTIVE):
        if subscription.end_date == datetime.date.today():
            subscription.status = SubscriptionStatus.INACTIVE
            subscription.save()
            # use celery task to send email
            send_email_task.delay(
                subject='Subscription Ended',
                message=f'Your subscription to {subscription.plan.name} has ended.',
                recipient_list=[subscription.user.email]
            )

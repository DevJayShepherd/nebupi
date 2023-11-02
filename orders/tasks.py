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

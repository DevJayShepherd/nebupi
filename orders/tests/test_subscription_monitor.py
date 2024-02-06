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
from django.test import TestCase

# users
from users.models import User

# orders
from orders.models import Plan, Subscription, SubscriptionStatus
from orders.tasks import monitor_subscriptions_task

from datetime import date, timedelta
from unittest.mock import patch


class MonitorSubscriptionsTaskTests(TestCase):

    def setUp(self):
        # Create a user and a plan for the subscriptions
        user = User.objects.create_user(
            email='testuser@asdf.com',
            password='12345'
        )
        user2 = User.objects.create_user(
            email='testuser2@asdf.com',
            password='12345'
        )
        user3 = User.objects.create_user(
            email='testuser3@asdf.com',
            password='12345'
        )

        plan = Plan.objects.create(name="Test Plan",
                                   price=10.00,
                                   tier=1,
                                   external_plan_id="test_plan")

        # Create a subscription that ends today
        self.subscription_today = Subscription.objects.create(
            subscription_id="test1",
            user=user,
            plan=plan,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today(),
            status=SubscriptionStatus.ACTIVE
        )

        # Create a subscription that ends tomorrow
        self.subscription_tomorrow = Subscription.objects.create(
            subscription_id="test2",
            user=user2,
            plan=plan,
            start_date=date.today() - timedelta(days=29),
            end_date=date.today() + timedelta(days=1),
            status=SubscriptionStatus.ACTIVE
        )

        # create a subscription that ended 3 days ago
        self.subscription_3_days_ago = Subscription.objects.create(
            subscription_id="test3",
            user=user3,
            plan=plan,
            start_date=date.today() - timedelta(days=33),
            end_date=date.today() - timedelta(days=3),
            status=SubscriptionStatus.ACTIVE
        )


    def test_subscription_ending_today(self):
        monitor_subscriptions_task()

        # Refresh the subscription from the database
        self.subscription_today.refresh_from_db()

        # verify that the status is still ACTIVE
        self.assertEqual(self.subscription_today.status, SubscriptionStatus.ACTIVE)


    @patch('users.tasks.send_email_task.delay')
    def test_subscription_ended_3_days_ago(self, mock_send_email):
        monitor_subscriptions_task()

        # Refresh the subscription from the database
        self.subscription_3_days_ago.refresh_from_db()

        # Check if the status has been updated to INACTIVE
        self.assertEqual(self.subscription_3_days_ago.status, SubscriptionStatus.INACTIVE)

        # Check if the email sending task was called
        mock_send_email.assert_called_once()

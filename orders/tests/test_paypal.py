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
from django.test import TestCase, RequestFactory

# orders
from orders.models import Subscription, Plan, SubscriptionStatus
from orders.paypal.paypal_helper import process_paypal_webhook

# users
from users.models import User

import json
import datetime
from unittest.mock import patch


class ProcessPaypalWebhookTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email='testuser@asdf.com',
            password='12345'
        )
        self.user2 = User.objects.create_user(
            email='testuser2@asdf.com',
            password='12345'
        )   
        self.new_subscriber1 = User.objects.create_user(
            email='new_subscriber1@asdf.com',
            password='12345'
        )
        self.new_subscriber2 = User.objects.create_user(
            email='new_subscriber2@asdf.com',
            password='12345'
        )
        self.plan_monthly = Plan.objects.create(
            name="Test Plan Monthly",
            price=10,
            tier=1,
            external_plan_id="monthly_plan_id"
        )
        self.subscription_monthly = Subscription.objects.create(
            subscription_id="test123",
            user=self.user,
            plan=self.plan_monthly,
            start_date="2021-01-01",
            end_date="2021-01-01",
            status="active"
        )
        self.plan_yearly = Plan.objects.create(
            name="Test Plan Yearly",
            price=10,
            tier=1,
            external_plan_id="yearly_plan_id"
        )
        self.subscription_yearly = Subscription.objects.create(
            subscription_id="test2",
            user=self.user2,
            plan=self.plan_yearly,
            start_date="2021-01-01",
            end_date="2021-01-01",
            status="active"
        )


    def test_invalid_json(self):
        request = self.factory.post('/webhook-endpoint/',
                                    data="invalid json}",
                                    content_type='application/json')
        response = process_paypal_webhook(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Invalid JSON'})


    def test_user_not_found(self):
        data = {
            "event_type": "BILLING.SUBSCRIPTION.ACTIVATED",
            "resource": {
                "id": "test123",
                "plan_id": "nonexistent123",
                "custom_id": "nonexistent@user.com"
            }
        }
        request = self.factory.post('/webhook-endpoint/',
                                    data=json.dumps(data),
                                    content_type='application/json')
        response = process_paypal_webhook(request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content), {'error': 'User not found'})


    def test_subscription_not_found(self):
        data = {
            "event_type": "PAYMENT.SALE.COMPLETED",
            "resource": {
                "id": "nonexistent123",
                "plan_id": "monthly_plan_id",
                "status": "ACTIVE",
                "custom": "new_subscriber1@asdf.com"
            }
        }
        request = self.factory.post('/webhook-endpoint/',
                                    data=json.dumps(data),
                                    content_type='application/json')
        response = process_paypal_webhook(request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content), {'error': 'Subscription not found'})


    def test_subscription_activated(self):
        end_date = datetime.date(2024, 11, 27)

        data = {
            "event_type": "BILLING.SUBSCRIPTION.ACTIVATED",
            "resource": {
                "id": "new_subscription_m_id",
                "plan_id": "monthly_plan_id",
                "custom_id": "new_subscriber1@asdf.com",
                "create_time": "2023-10-27T20:41:15Z",
                "billing_info": {
                    "next_billing_time": end_date.strftime("%Y-%m-%d") + "T10:00:00Z"
                }
            }
        }

        request = self.factory.post('/webhook-endpoint/',
                                    data=json.dumps(data),
                                    content_type='application/json')
        response = process_paypal_webhook(request)

        # verify that the subscription is created
        subscription = Subscription.objects.get(subscription_id=data['resource']['id'])

        self.assertEqual(subscription.status, SubscriptionStatus.ACTIVE)
        self.assertEqual(subscription.plan, Plan.objects.get(external_plan_id=data['resource']['plan_id']))
        self.assertEqual(subscription.user, User.objects.get(email=data['resource']['custom_id']))
        self.assertEqual(subscription.start_date, datetime.date(2023, 10, 27))
        self.assertEqual(subscription.end_date, end_date)
        self.assertEqual(response.status_code, 200)


    def test_plan_not_found(self):
        data = {
            "event_type": "BILLING.SUBSCRIPTION.RE-ACTIVATED",
            "resource": {
                "id": "test123",
                "plan_id": "nonexistent123",
                "custom_id": "testuser@asdf.com"
            }
        }
        request = self.factory.post('/webhook-endpoint/',
                                    data=json.dumps(data),
                                    content_type='application/json')
        response = process_paypal_webhook(request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content), {'error': 'Plan not found'})


    @patch('orders.paypal.paypal_helper.get_subscription')
    def test_payment_sale_completed(self, mock_get_subscription):
        end_date = datetime.date(2023, 10, 27)

        mock_get_subscription.return_value = {
            "billing_info": {
                "next_billing_time": end_date.strftime("%Y-%m-%d") + "T10:00:00Z"
            }
        }

        data = {
            "event_type": "PAYMENT.SALE.COMPLETED",
            "resource": {
                "id": "test123",
                "plan_id": "monthly_plan_id",
                "status": "ACTIVE",
                "custom": "testuser@asdf.com"
            }
        }
        request = self.factory.post('/webhook-endpoint/',
                                    data=json.dumps(data),
                                    content_type='application/json')
        response = process_paypal_webhook(request)
        self.subscription_monthly.refresh_from_db()
        self.assertEqual(self.subscription_monthly.status, "active")
        self.assertEqual(self.subscription_monthly.end_date, end_date)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'message': 'Subscription updated successfully'})


    @patch('orders.paypal.paypal_helper.send_email_task.delay')
    def test_payment_failed(self, mock_send_email):
        data = {
            "event_type": "BILLING.SUBSCRIPTION.PAYMENT.FAILED",
            "resource": {
                "id": "test123",
                "plan_id": "monthly_plan_id",
                "custom_id": "testuser@asdf.com"
            }
        }

        request = self.factory.post('/webhook-endpoint/',
                                    data=json.dumps(data),
                                    content_type='application/json')
        process_paypal_webhook(request)
        self.subscription_monthly.refresh_from_db()
        self.assertEqual(self.subscription_monthly.status, "past due")
        mock_send_email.assert_called_once()

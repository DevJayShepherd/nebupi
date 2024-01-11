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
from orders.stripe.stripe_helper import process_webhook

# users
from users.models import User

import json
import datetime
from unittest.mock import patch


class ProcessStripeWebhookTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email='testuser@asdf.com',
            password='12345'
        )
        self.new_subscriber1 = User.objects.create_user(
            email='new_subscriber1@asdf.com',
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


    def test_invalid_json(self):
        request = self.factory.post('/webhook-endpoint/',
                                    data="{'invalid' : 'payload'}",
                                    content_type='application/json')
        response = process_webhook(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Invalid payload'})


    @patch('orders.stripe.stripe_helper.stripe.Subscription.retrieve')
    def test_checkout_session_completed(self, mock_retrieve):
        start_timestamp = 1704833942
        end_timestamp = 1707512342

        mock_retrieve.return_value = {
            'current_period_start': start_timestamp,
            'current_period_end': end_timestamp,
            'items': {
                'data': [
                    {
                        'price': {
                            'id': 'monthly_plan_id'
                        }
                    }
                ]
            }
        }

        data = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'customer_details': {
                        'email': self.new_subscriber1.email
                    },
                    'subscription': 'new_sub_test_123'
                }
            }
        }
        request = self.factory.post('/webhook-endpoint/',
                                    data=json.dumps(data),
                                    content_type='application/json')
        response = process_webhook(request)

        subscription = Subscription.objects.get(user=self.new_subscriber1)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(subscription.plan, self.plan_monthly)
        self.assertEqual(subscription.status, SubscriptionStatus.ACTIVE)
        self.assertEqual(subscription.subscription_id, 'new_sub_test_123')
        self.assertEqual(subscription.start_date, datetime.date.fromtimestamp(start_timestamp))
        self.assertEqual(subscription.end_date, datetime.date.fromtimestamp(end_timestamp))


    @patch('orders.stripe.stripe_helper.stripe.Subscription.retrieve')
    def test_checkout_session_completed_plan_not_found(self, mock_retrieve):
        start_timestamp = 1704833942
        end_timestamp = 1707512342

        mock_retrieve.return_value = {
            'current_period_start': start_timestamp,
            'current_period_end': end_timestamp,
            'items': {
                'data': [
                    {
                        'price': {
                            'id': 'nonexistent123'
                        }
                    }
                ]
            }
        }

        data = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'customer_details': {
                        'email': self.new_subscriber1.email
                    },
                    'subscription': 'new_sub_test_123'
                }
            }
        }
        request = self.factory.post('/webhook-endpoint/',
                                    data=json.dumps(data),
                                    content_type='application/json')
        response = process_webhook(request)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content), {'error': 'Plan not found'})


    def test_invoice_paid(self):
        end_timestamp = 1707512342
        data = {
            'type': 'invoice.paid',
            'data': {
                'object': {
                    'subscription': self.subscription_monthly.subscription_id,
                    'customer_details': {
                        'email': self.user.email
                    },
                    'lines': {
                        'data': [
                            {
                                'period': {
                                    'end': end_timestamp
                                }
                            }
                        ]
                    }
                }
            }
        }
        request = self.factory.post('/webhook-endpoint/',
                                    data=json.dumps(data),
                                    content_type='application/json')
        response = process_webhook(request)

        self.subscription_monthly.refresh_from_db()
        self.assertEqual(self.subscription_monthly.status, SubscriptionStatus.ACTIVE)
        self.assertEqual(self.subscription_monthly.end_date, datetime.date.fromtimestamp(end_timestamp))
        self.assertEqual(response.status_code, 200)


    def test_invoice_payment_failed(self):
        data = {
            'type': 'invoice.payment_failed',
            'data': {
                'object': {
                    'subscription': self.subscription_monthly.subscription_id,
                    'customer_details': {
                        'email': self.user.email
                    }
                }
            }
        }
        request = self.factory.post('/webhook-endpoint/',
                                    data=json.dumps(data),
                                    content_type='application/json')
        response = process_webhook(request)

        self.subscription_monthly.refresh_from_db()
        self.assertEqual(self.subscription_monthly.status, SubscriptionStatus.PAST_DUE)
        self.assertEqual(response.status_code, 200)

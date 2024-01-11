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


from django.db import models
from users.models import User


class PaymentGatewayChoices(models.TextChoices):
    STRIPE = 'STRIPE'
    PAYPAL = 'PAYPAL'


class Plan(models.Model):
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tier = models.PositiveIntegerField()
    external_plan_id = models.CharField(max_length=255)
    payment_gateway = models.CharField(max_length=10, choices=PaymentGatewayChoices.choices)

    def __str__(self):
        return self.name


class Product(models.Model):
    product_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class SubscriptionStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    INACTIVE = 'inactive', 'Inactive'
    PAST_DUE = 'past due', 'Past Due'


class Subscription(models.Model):
    subscription_id = models.CharField(max_length=255, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=15,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.INACTIVE
    )

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    def is_active(self):
        return self.status == SubscriptionStatus.ACTIVE


class Transaction(models.Model):
    TRANSACTION_CHOICES = (
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending'),
    )

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=TRANSACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subscription.user.username} - {self.amount} - {self.status}"

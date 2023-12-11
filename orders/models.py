from django.db import models
from users.models import User


class PlanFrequencyChoices(models.TextChoices):
    MONTHLY = 'MONTHLY'
    YEARLY = 'YEARLY'


class Plan(models.Model):
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tier = models.PositiveIntegerField()
    billing_frequency = models.CharField(max_length=10, choices=PlanFrequencyChoices.choices)
    external_plan_id = models.CharField(max_length=255)

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

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


"""
URL configuration for ready_saas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# django
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views

# users
from users.views import SignUpView, EmailLoginView
from users.forms import AsyncPasswordResetForm, CustomAuthenticationForm, CustomSetPasswordForm

# orders
from orders.views import (
    pricing, checkout, checkout_product, user_subscription,
    paypal_webhook_listener, paypal_orders_create, paypal_orders_capture,
    stripe_checkout_session_create, stripe_webhook_listener
)

# ready_saas
from ready_saas.views import landing, dashboard

# email login
from sesame.views import LoginView

import os
import environ


# Setup environment variables with fallback to .env file
env = environ.Env(
    DEBUG=(bool, False)
)


urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Django authentication urls
    # signup and login with email and password, logout, password reset, etc.
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(form_class=CustomSetPasswordForm), name='password_reset_confirm'),
    path('accounts/login/', auth_views.LoginView.as_view(authentication_form=CustomAuthenticationForm), name='login'),
    path("accounts/signup/", SignUpView, name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("verify/", TemplateView.as_view(template_name="email_verification_sent.html"), name="email_verification_sent"),
    path('password_reset/', auth_views.PasswordResetView.as_view(form_class=AsyncPasswordResetForm), name='password_reset'),


    # Email login (django-sesame)
    # login with email link
    path("email/login/", EmailLoginView.as_view(), name="email_login"),
    path("email/login/auth/", LoginView.as_view(), name="email_login_auth"),


    # Payments and subscriptions
    # pages
    path("pricing/", pricing, name="pricing"),
    path("checkout/subscriptions/<int:plan_id>/", checkout, name="checkout"),
    path("checkout/products/<str:product_id>/", checkout_product, name="checkout_product"),
    path("thank_you/", TemplateView.as_view(template_name="thank_you.html"), name="thank_you"),
    path('user/subscription/', user_subscription, name='user_subscription'),
    # Paypal
    # subscription webhooks
    path("paypal/event", paypal_webhook_listener, name="paypal-event"),
    # one time purchase
    path("paypal/orders/create/", paypal_orders_create, name="paypal_order_create"),
    path("paypal/orders/<str:order_id>/capture/", paypal_orders_capture, name="paypal_order_capture"),
    # Stripe
    path("stripe/checkout-session/create/", stripe_checkout_session_create, name="stripe_checkout_session_create"),
    # subscription webhooks
    path("stripe/webhook", stripe_webhook_listener, name="stripe-event"),


    # app pages
    path("", landing, name="landing"),
    path("dashboard/", dashboard, name="dashboard"),

    # ============= #
    # Optional Apps - Comment out as needed
    # ============= #
    # waitlist
    path('waitlist/', include('waitlist.urls')),

    # blog
    path('blog/', include('blog.urls')),


    # Error pages:
    # Uncomment the two lines below for testing purposes only
    # path('test_404/', TemplateView.as_view(template_name='404.html')),
    # path('test_500/', TemplateView.as_view(template_name='500.html')),
]

debug_value = os.getenv('DEBUG', env('DEBUG'))
if debug_value == 'on' or debug_value is True:
    urlpatterns += [
        path('__reload__/', include('django_browser_reload.urls')),
    ]

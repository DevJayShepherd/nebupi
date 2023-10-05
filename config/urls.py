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

# users
from users.views import SignUpView
from users.views import EmailLoginView

# email login
from sesame.views import LoginView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/signup/", SignUpView, name="signup"),
    path("login/", EmailLoginView.as_view(), name="email_login"),
    path("login/auth/", LoginView.as_view(), name="login"),
    path("dashboard/", TemplateView.as_view(template_name="dashboard.html"), name="dashboard"),
    path("", TemplateView.as_view(template_name="landing.html"), name="landing"),
    path("verify/", TemplateView.as_view(template_name="email_verification_sent.html"), name="email_verification_sent"),
]

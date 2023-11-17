from django.urls import path
from .views import join_waitlist


urlpatterns = [
    path('join/', join_waitlist, name='join_waitlist'),
]

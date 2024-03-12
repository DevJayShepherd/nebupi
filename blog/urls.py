from django.urls import path
from blog.views import blog_post


urlpatterns = [
    path('<slug>', blog_post, name='blog_post'),
]

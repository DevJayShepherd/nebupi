from django.shortcuts import render

# blog
from blog.models import BlogPost


def blog_post(request, slug):
    blog_post = BlogPost.objects.get(slug=slug)
    return render(request, 'blog/post.html', {"blog_post": blog_post})
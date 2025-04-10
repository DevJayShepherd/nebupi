from django.db import models
from django.utils.translation import gettext_lazy as _

from datetime import datetime

from autoslug.fields import AutoSlugField


class BlogPostQueryset(models.QuerySet):

    def published(self):
        return self.filter(published=True)

    def draft(self):
        return self.filter(published=False)


class BlogPost(models.Model):
    title = models.CharField(_('title'), max_length=255)
    slug = AutoSlugField(_('slug'), populate_from='title', unique=True)
    content = models.TextField(_('content'), blank=True, null=True)
    description = models.TextField(_('description'), blank=True, null=True)
    keywords = models.TextField(_('keywords'), blank=True, null=True)
    published = models.BooleanField(_('published'), default=False)

    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    pub_date = models.DateTimeField(_('publish date'), blank=True, null=True)

    class Meta:
        verbose_name = _('blog post')
        verbose_name_plural = _('blog posts')
        ordering = ['pub_date']


    def save(self, *args, **kwargs):
        """
        Set publish date to the date when the post's published status is switched to True,
        reset the date if the post is unpublished
        """
        if self.published and self.pub_date is None:
            self.pub_date = datetime.now()
        elif not self.published and self.pub_date is not None:
            self.pub_date = None
        super().save(*args, **kwargs)


    def __str__(self):
        return self.title

from django import template
from django.utils.safestring import mark_safe
import markdown as md

register = template.Library()

@register.filter
def markdown_to_html(text):
    return mark_safe(md.markdown(text, extensions=["fenced_code", "codehilite"]))

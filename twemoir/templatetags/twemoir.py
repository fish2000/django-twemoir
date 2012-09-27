
from django import template

register = template.Library()

@register.inclusion_tag('twemoir/tags/chapter_header.html')
def chapter_header(chapter_title, chapter_idx):
    return {
        'title':    unicode(chapter_title),
        'idx':      int(chapter_idx), }

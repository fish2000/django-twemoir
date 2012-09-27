
import re
from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

from BeautifulSoup import BeautifulSoup
from twemoir.forms import TMBoxForm

register = template.Library()

@register.inclusion_tag('twemoir/tags/chapter_header.html')
def chapter_header(chapter_title, chapter_idx):
    return {
        'title':    unicode(chapter_title),
        'idx':      int(chapter_idx),
    }

@register.inclusion_tag('twemoir/tags/draft_editor_codemirror2.html')
def draft(editor_form=None):
    return {
        'form': editor_form,
    }


@register.inclusion_tag('twemoir/tags/draft_editor_codemirror2.html')
def box(editor_form=None):
    return {
        'form': editor_form,
    }

suffixer = re.compile('^(?<!http:).+?\.(.{1,8})$')

@register.simple_tag(name='form_css')
def form_css(form=None):
    if form is None:
        form = TMBoxForm()
    if hasattr(form, 'media'):
        noncss = set()
        css = set(filter(
            lambda link: BeautifulSoup(link).findAll('link',
                attrs={ 'href': lambda href: href.lower().endswith('css'), }),
                    form.media['css'].render_css()))
        
        for noncsslink in filter(
            lambda link: not link.attrMap.get('href').lower().endswith('css'), map(
                lambda htmlfrag: BeautifulSoup(htmlfrag).findAll('link',
                    attrs={ 'href': suffixer }).pop(), list(form.media['css'].render_css()))):
            noncsslink['type'] = suffixer.sub('text/\g<1>', noncsslink['href'])
            noncss.add(unicode(noncsslink))
        
        return list(css | noncss)
    return []

@register.simple_tag()
def form_js(form=None):
    if hasattr(form, 'media'):
        return form.media['js'].render()
    return ''


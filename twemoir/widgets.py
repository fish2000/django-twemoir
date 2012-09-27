
import os, functools
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

static_url = lambda *u: os.path.join(settings.STATIC_URL, 'twemoir', *u)
static_css = functools.partial(static_url, *['css'])
static_less = functools.partial(static_url, *['less'])
static_js = functools.partial(static_url, *['js'])

class TMSentenceTokenizerTextbox(forms.Textarea):
    
    cssclass = 'my-memoirs'
    
    class Media:
        css = { 'all': [
            static_less('textbox.less')] }
        js = [
            static_js('textbox.js')]
    
    def __init__(self, language=None, attrs={}):
        self.language = language or settings.LANGUAGE_CODE[:2]
        super(TMSentenceTokenizerTextbox, self).__init__(attrs=attrs)
    
    def render(self, name, values, attrs={}):
        cssclassout = cssclass = attrs.get('class', '').strip()
        if self.cssclass not in cssclass:
            cssclassout = "%s %s" % (cssclass, self.cssclass)
        attrs.update({ 'class': cssclassout.strip(), })
        return mark_safe(super(TMSentenceTokenizerTextbox, self).render(name, values, attrs))

    

from django import forms
from django.contrib.webdesign import lorem_ipsum

from form_utils.forms import BetterForm
from codemirror2.widgets import CodeMirrorEditor

from twemoir.widgets import TMSentenceTokenizerTextbox

""" See Also: https://github.com/sk1p/django-codemirror2 """

class TMDraftForm(BetterForm):
    
    my_twitters = forms.CharField(
        initial="YO DOGG",
        widget=CodeMirrorEditor(
            options={ 'mode': 'mustache', }))


class TMBoxForm(BetterForm):
    
    my_twitters = forms.CharField(
        label='', help_text='',
        initial=lorem_ipsum.COMMON_P,
        widget=TMSentenceTokenizerTextbox)
    
    class Meta:
        fieldsets = [
            (None, {
                'fields': ['my_twitters',],
                'legend': "Yo Dogg, I Heard You Like Feelins",
            }),
        ]

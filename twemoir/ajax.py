
import logging
logg = logging.getLogger(__name__)

from django.core.signing import Signer

import nltk
from dajax.core import Dajax
from dajaxice.core import dajaxice_functions
from threading import local

sentencer = local()
sentencery = lambda: nltk.data.load('tokenizers/punkt/english.pickle')
sentencer.value = sentencery()

def sentencing(request, txt=''):
    if not hasattr(sentencer, 'value'):
        logg.warning("Reloading Punkt data from XHR callback!")
    
    sentencerizer = lambda: getattr(sentencer, 'value', sentencery())
    signer = Signer()
    dajax = Dajax()
    sn = []
    js_callback = "$$('#q')._callback"
    
    if len(txt) > 1:
        sentences = sentencerizer().tokenize(txt)
        for sentence in sentences:
            sn.append(dict(
                chunklength=len(sentence),
                chunk=sentence))
        
    dajax.add_data({ 'data': sn, 'signature': signer.signature(txt), }, 
        js_callback)
    
    return dajax.json()

dajaxice_functions.register(sentencing)
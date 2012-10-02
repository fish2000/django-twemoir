
from django.core.signing import Signer

from django.db import models
from django.db.models import signals

class CharSignatureField(models.CharField):
    """
    Store the cryptographic signature for an instance
    of models.CharField (on the same model).
    
    """
    __metaclass__ = models.SubfieldBase
    
    # SIGNATURE_LENGTH is set to 27, which is the value of:
    # >>> len(Signer().signature(x))
    # ... for any string x. Confusingly, the actual number
    # is never explicitly specified by Django Inc -- neither
    # in the docs nor somewhere the code itself. As such the
    # value '27' was empirically deduced, and is probably
    # subject to the implementation-detail whims of the
    # Django developers.
    
    SIGNATURE_LENGTH = 27
    
    # SIGNATURE_FIELD_SALT is a last-resort default salt, which
    # can be overridden by either a) defining a string value of
    # the same name -- SIGNATURE_FIELD_SALT -- in your Django
    # settings, or b) passing a 'salt' kwarg when constructing
    # your CharSignatureField.
    
    SIGNATURE_FIELD_SALT = 'yo dogg what it is'
    
    def __init__(self, signatory=None, **kwargs):
        self.signatory = signatory
        
        if self.signatory:
            from django.conf import settings
            SignerClass = kwargs.pop('signer_class', Signer)
            self.salt = kwargs.pop('salt',
                getattr(settings, 'SIGNATURE_FIELD_SALT',
                    self.SIGNATURE_FIELD_SALT))
            self.signer = SignerClass(salt=self.salt)
        
        else:
            raise AttributeError(
                "CharSignatureField can't be defined without "
                "a 'signatory' parameter, naming the CharField "
                "on the same model, containing data to be signed.")
        
        kwargs.setdefault('max_length', self.SIGNATURE_LENGTH)
        kwargs.setdefault('db_index', True)
        kwargs.setdefault('editable', False)
        kwargs.setdefault('blank', True)
        kwargs.setdefault('null', True)
        super(CharSignatureField, self).__init__(**kwargs)
    
    def signature(self, instance):
        if hasattr(self.signatory, 'name'):
            signatory = str(self.signatory.name)
        else:
            signatory = self.signatory
        
        if not hasattr(instance, signatory):
            raise AttributeError(
                "CharSignatureField can't find signatory data "
                "on this model with field name: %s" % signatory)
        return self.signer.signature(
            getattr(instance, signatory))
    
    def get_db_prep_value(self, value, connection=None, prepared=False):
        if not value:
            return u''
        return unicode(value)
    
    def value_to_string(self, instance):
        return self.get_db_prep_value(self.signature(instance))
    
    def contribute_to_class(self, cls, name):
        super(CharSignatureField, self).contribute_to_class(cls, name)
        signals.post_init.connect(self.refresh_signature, sender=cls,
            dispatch_uid='charsignaturefield-post-init')
        signals.pre_save.connect(self.refresh_signature, sender=cls,
            dispatch_uid='charsignaturefield-pre-save')
    
    def refresh_signature(self, **kwargs): # signal, sender, instance
        if not kwargs.get('raw', False):
            instance = kwargs.get('instance')
            setattr(instance, self.name, self.signature(instance))
    
    def get_internal_type(self):
        return "CharField"
    
    def _south_field_triple(self):
        from south.modelsinspector import introspector
        args, kwargs = introspector(self)
        return ('twemoir.modelfields.%s' % self.__class__.__name__, args, kwargs)


try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules(
        rules = [
            ((CharSignatureField,), [], {
                'signatory': ('text', { 'is_value': True, }),
            }),
        ], patterns = [
            '^twemoir\.modelfields\.CharSignatureField',
        ]
    )

# South introspection
from twemoir.lib.states2.fields import StateField # solely to assuage South
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules(
        [
            (
                (StateField,), [], {
                    'max_length': [100, { "is_value": True, }],
                }
            )
        ], ["^states2\.fields\.StateField",
            "^lib\.states2\.fields\.StateField",
            "^twemoir\.lib\.states2\.fields\.StateField"]
    )


from django.utils.functional import SimpleLazyObject
from appconf import AppConf

try:
    from django.utils.functional import empty
except ImportError:
    empty = None

class LazyDict(SimpleLazyObject, dict):
    """ Lazy dict initialization. """
    
    def __len__(self):
        if self._wrapped is empty:
            self._setup()
        return len(self._wrapped)
    
    def __getitem__(self, name):
        if self._wrapped is empty:
            self._setup()
        return self._wrapped[name]

    def __setitem__(self, name, value):
        if self._wrapped is empty:
            self._setup()
        self._wrapped[name] = value
    
    def __iter__(self):
        if self._wrapped is empty:
            self._setup()
        return self._wrapped
    
    def __contains__(self, item):
        if self._wrapped is empty:
            self._setup()
        return (item in self._wrapped)

class TwemoirAppConf(AppConf):
    """
    Pre-django-appconf, this was dealt with by defining these functions
    at the bottom of twemoir/models.py:
    
        
        def AUTHOR_CREDENTIALS():
            return TMUserKeyset.objects.author_credentials()

        def AUTHOR_USER_NAME():
            return TMUserKeyset.objects.author_user_name()

    ... which would be called as part of any function directly leading to
    the invocation of the Twitter API. The call delivered the credentials
    like so:
    
        will_call_twitter(something, somevalue=something_else,
            **AUTHOR_CREDENTIALS())
    
    """
    USER = 'twemoir'
    
    AUTHOR_CREDENTIALS = None
    AUTHOR_USER_NAME = None
    
    TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
    TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
    TWITTER_AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'

    class Meta:
        prefix = 'twemoir'
        
    def configure_author_credentials(self, value):
        def _author_credentials():
            from twemoir import models as tm
            return tm.TMUserKeyset.objects.author_credentials()
        return LazyDict(_author_credentials)
    
    def configure_author_user_name(self, value):
        def _author_user_name():
            from twemoir import models as tm
            return tm.TMUserKeyset.objects.author_user_name()
        return SimpleLazyObject(_author_user_name)


#settings = SimpleLazyObject(lambda: TwemoirAppConf())
settings = TwemoirAppConf()
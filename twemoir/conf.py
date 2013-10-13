
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
    
    def __repr__(self):
        if self._wrapped is empty:
            self._setup()
        return repr(self._wrapped)
    
    def as_dict(self):
        if self._wrapped is empty:
            self._setup()
        return self._wrapped

class TwemoirAppConf(AppConf):
    
    USER = 'twitter-author-username'
    
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
            return dict(tm.TMUserKeyset.objects.author_credentials())
        return LazyDict(_author_credentials)
    
    def configure_author_user_name(self, value):
        def _author_user_name():
            from twemoir import models as tm
            return tm.TMUserKeyset.objects.author_user_name()
        return SimpleLazyObject(_author_user_name)

settings = TwemoirAppConf()

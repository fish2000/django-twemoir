
from django.utils.functional import SimpleLazyObject
from appconf import AppConf

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
    AUTHOR_CREDENTIALS = None
    AUTHOR_USER_NAME = None
    
    TWITTER_REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
    TWITTER_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
    TWITTER_AUTHORIZE_URL = 'https://api.twitter.com/oauth/authorize'

    class Meta:
        prefix = 'twemoir'
        
    def configure_author_credentials(self, value):
        from twemoir.models import TMUserKeyset
        return TMUserKeyset.objects.author_credentials()
    
    def configure_author_user_name(self, value):
        from twemoir.models import TMUserKeyset
        return TMUserKeyset.objects.author_user_name()


settings = SimpleLazyObject(lambda: TwemoirAppConf())
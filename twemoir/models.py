
import sys, threading
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db import transaction
from delegate import delegate, DelegateManager
from docfield.modelfields import JSONField

from django.contrib.auth.models import User
from tagging.fields import TagField
from tagging.models import Tag as Tagg

from twemoir.conf import settings
from twemoir.managers import TaggedManager, TaggedQuerySet
from twemoir.modelfields import CharSignatureField

# for TMStagedTweet and TMStagedDraft
from twemoir.lib.states2.models import (StateMachine, StateDefinition,
                                        StateTransition, StateModel)


class TMTweetQuerySet(TaggedQuerySet):
    @delegate
    def contains(self, search_string):
        """ Filter TMTweets by tweet content. """
        return self.filter(text__icontains=search_string)
    
    @delegate
    def max_id(self, user_id=None):
        """ A misnamed function - get a number lower than the lowest
        TMTweet's Twitter status ID. """
        try:
            subset = user_id and self.filter(user_id=user_id) or self.all()
            return (subset.aggregate(max_id=models.Min('status_id'))['max_id'] - 1)
        except ObjectDoesNotExist:
            return 0
    
    @delegate
    def since_id(self, user_id=None):
        """ A misnamed function - get the highest TMTweet's
        Twitter status ID. """
        try:
            subset = user_id and self.filter(user_id=user_id) or self.all()
            return subset.aggregate(since_id=models.Max('status_id'))['since_id']
        except ObjectDoesNotExist:
            return 0


class TMTweetManager(TaggedManager):
    __queryset__ = TMTweetQuerySet
    
    def sync(self, user_id_or_username=None):
        """ Sync all tweets by the Twitter author as local TMTweets. """
        from twemoir.utils import TMUserTweets
        if not user_id_or_username:
            user_id_or_username = settings.AUTHOR_USER_NAME
        author_credentials = settings.AUTHOR_CREDENTIALS
        tweets = TMUserTweets(user_id_or_username, verbose=True,
            **author_credentials)
        self.load_tweets(tweets)
    
    def sync_latest(self, user_id_or_username=None):
        """ Sync the latest tweets by the Twitter author locally as TMTweets. """
        from twemoir.utils import TMUserTweets
        if not user_id_or_username:
            user_id_or_username = settings.AUTHOR_USER_NAME
        author_credentials = settings.AUTHOR_CREDENTIALS
        tweets = TMUserTweets(user_id_or_username, verbose=True, since_id=self.since_id(),
            **author_credentials)
        self.load_tweets(tweets)
    
    def load_tweet(self, status_id):
        """ Load a single tweet by its Twitter status ID,
        and save it locally as a TMTweet instance. """
        import twitter
        tweet = twitter.GetStatus(status_id)
        self.load_tweets([tweet])
    
    def load_tweets(self, tweets):
        """ Saves a list of twitter.Statuses as TMTweets. """
        import warnings
        from twemoir.utils import nonentitize
        
        for tweet in tweets:
            cleaned_text = nonentitize(tweet.text)
            if len(cleaned_text) > 140:
                warnings.warn('OMG: Long tweet text (%d chars) in tweet %s: %s' % (
                    len(tweet.text), tweet.id, cleaned_text), UserWarning)
            
            tmtweet, is_new = self.get_or_create(
                status_id=tweet.id,
                user_id=tweet.user.id,
                defaults=dict(
                    text=unicode(cleaned_text)[:150]
                ),
            )
            
            tmtweet.tweet_struct = tweet.AsDict()
            tmtweet.save()
            tmtweet.tags = [str(hashtag.text) for hashtag in tweet.hashtags]
            tmtweet.save()


class TMTweet(models.Model):
    
    objects = TMTweetManager()
    
    status_id = models.BigIntegerField(
        verbose_name="Twitter Status ID",
        db_index=True,
        editable=False,
        blank=False,
        null=False)
    
    user_id = models.BigIntegerField(
        verbose_name="Twitter User ID",
        db_index=True,
        editable=False,
        blank=False,
        null=False)
    
    text = models.CharField(
        verbose_name="Tweet Text",
        max_length=150,
        db_index=True,
        blank=False,
        null=False)
    
    tweet_struct = JSONField(
        verbose_name="Tweet Structure (from Twitter's API)",
        editable=True,
        blank=True,
        null=True)
    
    _tags = TagField(
        verbose_name="Hashtags Contained in Tweet",
        db_index=True,
        editable=True,
        blank=True,
        null=True)
    
    class Meta:
        abstract = False
        ordering = ('status_id','user_id')
        verbose_name = "Author Tweet"
        verbose_name_plural = "Author Tweets"
    
    def _get_tags(self):
        """ Get tagging.models.Tags for a tweet's hashtags. """
        return Tagg.objects.get_for_object(self)
    
    def _set_tags(self, taglist):
        """ Set the hashtags. """
        if type(taglist) == type([]):
            Tagg.objects.update_tags(self, " ".join(taglist))
            self._tags = " ".join(taglist)
        else:
            Tagg.objects.update_tags(self, taglist)
            self._tags = taglist
    
    def _get_tagstring(self):
        """ Return all hashtags as a single string. """
        return unicode(self._tags)
    
    tags = property(_get_tags, _set_tags)
    tagstring = property(_get_tagstring)
    
    def __getattr__(self, name):
        """ Try getting non-model attributes by name from
        the TMTweet.tweet_struct dict. """
        
        try:
            return super(TMTweet, self).__getattr__(name)
        except AttributeError, err:
            if self.tweet_struct is not None:
                if name in self.tweet_struct:
                    return eval(self.tweet_struct).get(name)
                else:
                    raise AttributeError(err)
            else:
                raise AttributeError(err)
        return super(TMTweet, self).__getattr__(name)
    
    def __str__(self):
        """ Return the tweet as UTF-8. """
        return self.text.encode('UTF-8', 'replace')
    
    def __unicode__(self):
        """ Return the tweet as Unicode. """
        return self.text


""" The GAL: Global API Lock. The GIL's red-headed stepchild. """
GAL = threading.Lock()

class TMStagedTweetDFARemix(StateMachine):
    log_transitions = True # sure, sounds great... but how??
    
    # Staged tweet states
    
    class initial(StateDefinition):
        description = """ Staged tweet instance initialized """
        initial = True
    
    class will_not_tweet(StateDefinition):
        description = """ Tweet is not ready to post """
    
    class will_tweet(StateDefinition):
        description = """ Tweet will post on next signal! """
        
        def handler(self, instance):
            pass
    
    class tweeting(StateDefinition):
        description = """ Tweet is locked by signalqueue for posting """
        
        def handler(self, instance):
            from twemoir.utils import TMUserStatusUpdate
            import twitter, traceback
            
            ''' exclusively lock the outbound API posting process
            and block execution for however long we need to,
            so as not to exceed Twitter's rate limits. '''
            GAL.acquire()
            
            try:
                author_credentials = settings.AUTHOR_CREDENTIALS
                tweet = TMUserStatusUpdate(instance.text, verbose=True,
                    **author_credentials)
                instance.user_id = long(tweet.user.id)
                instance.tweet_struct = tweet.AsDict()
                instance.save()
            
            except twitter.TwitterError:
                (exc_type, exc_value, tb) = sys.exc_info()
                print "* A Twitter API %s was caught while tweeting:" % exc_type.__name__
                print "* '%s'" % exc_value
                print ""
                print traceback.format_exc()
                print ""
                
                instance.make_transition('duckpunch', None)
            
            except Exception:
                (exc_type, exc_value, tb) = sys.exc_info()
                print "* A non-TwitterError %s was caught while tweeting:" % exc_type.__name__
                print "* '%s'" % exc_value
                print ""
                print traceback.format_exc()
                print ""
                
                instance.make_transition('failwhale', None)
            
            else:
                # Tweet went up OK!
                instance.make_transition('verify', None)
            
            finally:
                ''' Release the outbound API lock. '''
                GAL.release()
    
    class did_not_tweet(StateDefinition):
        description = """ Tweet failed to post """
    
    class did_not_tweet_but_will_try_again(StateDefinition):
        description = """ Tweet failed to post, but will be readied for another attempt """
        
        def handler(self, instance):
            ''' TODO:
            Update the rate limit value in the outbound API
            posting process (which is a Twitter API call
            in its own right) '''
            pass
    
    class did_tweet(StateDefinition):
        description = """ Tweet has been successfully posted! """
    
    # Staged tweet state transitions
    
    class disqualify(StateTransition):
        description = """ Mark this staged tweet as unfit for posting """
        from_state =    'initial'
        to_state =      'will_not_tweet'
    
    class stage(StateTransition):
        description = """ Mark this staged tweet as ready to post """
        from_state =    'initial'
        to_state =      'will_tweet'
    
    class tweet(StateTransition):
        description = """ Post the staged tweet to twitter! """
        from_state =    'will_tweet'
        to_state =      'tweeting'
        
        def has_permission(self, instance, user):
            # for now, check all tweets -- add per-user stuff later
            return not TMStagedTweet.objects.tweeting()
    
    class verify(StateTransition):
        description = """ Mark the staged tweet a successful Twitter status update """
        from_state =    'tweeting'
        to_state =      'did_tweet'
    
    class failwhale(StateTransition):
        description = """ Mark the staged tweet as a failed post """
        from_state =    'tweeting'
        to_state =      'did_not_tweet'
    
    class duckpunch(StateTransition):
        description = """ Mark the staged tweet as an unsuccessful post that will be reattempted """
        from_state =    'tweeting'
        to_state =      'did_not_tweet_but_will_try_again'
    
    class restage(StateTransition):
        description = """ Restage the unsuccessfully-posted tweet """
        from_state =    'did_not_tweet_but_will_try_again'
        to_state =      'will_tweet'


class TMStagedTweetQuerySet(TaggedQuerySet):
    
    @delegate
    def tweeting(self):
        return self.filter(state='tweeting').exists()
    
    @delegate
    def make_transition(self, trans, user=None):
        import states2.exceptions
        failures = set()
        tweets = self.all()
        
        for tweet in tweets.select_for_update():
            with transaction.commit_manually():
                try:
                    tweet.make_transition(trans, user)
                except states2.exceptions.TransitionException:
                    failures.add(tweet.id)
                finally:
                    transaction.commit()
        
        return tweets.exclude(id__in=failures)

class TMStagedTweetManager(TaggedManager):
    __queryset__ = TMStagedTweetQuerySet

class TMStagedTweet(StateModel):
    
    objects = TMStagedTweetManager()
    
    Machine = TMStagedTweetDFARemix
    
    user_id = models.BigIntegerField(
        verbose_name="Twitter User ID",
        db_index=True,
        editable=False,
        blank=True,
        null=True)
    
    text = models.CharField(
        verbose_name="Tweet Text",
        max_length=150,
        db_index=True,
        blank=False,
        null=False)
    
    signature = CharSignatureField(
        verbose_name="Tweet Text Cryptographic Signature",
        salt="SALT THE SNAIL!! HYAA!! HYAAAAAA!!!!",
        signatory='text')
    
    tweet_struct = JSONField(
        verbose_name="Tweet Structure (from Twitter's API)",
        editable=True,
        blank=True,
        null=True)
    
    class Meta:
        abstract = False
        verbose_name = "Staged Tweet"
        verbose_name_plural = "Staged Tweet Objects"
    
    def check_signature(self):
        from django.core.signing import BadSignature
        signer = self._meta.get_field('signature').signer
        
        try:
            return signer.unsign(u"%s:%s" % (self.text, self.signature)) == self.text
        except BadSignature:
            return False
        
        return False


class TMKeyset(models.Model):
    
    key = models.CharField(
        verbose_name="Key",
        max_length=255,
        blank=False,
        null=False)
    
    secret = models.CharField(
        verbose_name="Secret",
        max_length=255,
        blank=False,
        null=False)
    
    class Meta:
        abstract = True
        unique_together = ('key','secret')
        verbose_name = "Keyset"
        verbose_name_plural = "Keysets"


class TMAppKeysetQuerySet(models.query.QuerySet):
    pass

class TMAppKeysetManager(DelegateManager):
    __queryset__ = TMAppKeysetQuerySet

class TMAppKeyset(TMKeyset):
    
    objects = TMAppKeysetManager()
    
    app_name = models.CharField(
        verbose_name="Twitter App Name",
        max_length=255,
        blank=True,
        null=True)
    
    owner = models.OneToOneField(User,
        related_name='app_keyset',
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    
    callback_url = models.CharField(
        verbose_name="Callback URL",
        max_length=255,
        blank=True,
        null=True)
    
    def _get_consumer(self):
        import oauth2 as oauth
        return oauth.Consumer(
            unicode(self.key), unicode(self.secret))
    
    def _get_client(self):
        import oauth2 as oauth
        return oauth.Client(
            self._get_consumer())
    
    def _get_request_token(self,
        url=settings.TWITTER_REQUEST_TOKEN_URL, method="GET"):
        import urlparse
        client = self._get_client()
        resp, content = client.request(url, method)
        request_token = dict(urlparse.parse_qsl(content))
        return request_token
    
    def _get_request_token_with_callback(self, callback,
        url=settings.TWITTER_REQUEST_TOKEN_URL, method="POST"):
        import urlparse, urllib
        client = self._get_client()
        resp, content = client.request(url, method,
            body=urllib.urlencode({ 'oauth_callback': callback, }))
        request_token = dict(urlparse.parse_qsl(content))
        
        callback_for_reals = request_token.get('oauth_callback_confirmed') == 'true'
        if not callback_for_reals:
            print "--- THIS CALLBACK SUCKS!!"
        else:
            print "*** I FUCKING LOVE WHAT HAPPENED WITH THIS CALLBACK!!"
        return request_token
    
    class Meta:
        abstract = False
        order_with_respect_to = 'owner'
        unique_together = ('key','secret')
        verbose_name = "Application Keyset"
        verbose_name_plural = "Application Keysets"
    
    def __repr__(self):
        return "<TMAppKeyset ID:%s>" % self.pk
    
    def __str__(self):
        """ Return the app name (or pk-label) as UTF-8. """
        if self.app_name:
            return self.app_name.encode('UTF-8', 'replace')
        return repr(self)
    
    def __unicode__(self):
        """ Return the app name (or pk-label) as Unicode. """
        if self.app_name:
            return self.app_name
        return unicode(repr(self))


class TMUserKeysetQuerySet(models.query.QuerySet):
    pass

class TMUserKeysetManager(DelegateManager):
    __queryset__ = TMUserKeysetQuerySet
    
    def get_author_user_keyset(self):
        """ Hardcoded for now. """
        return self.get(user_name='twemoir')
    
    def author_credentials(self):
        return self.get_author_user_keyset().credentials
    def author_user_name(self):
        return self.get_author_user_keyset().user_name

class TMUserKeyset(TMKeyset):
    
    objects = TMUserKeysetManager()
    
    app_keyset = models.ForeignKey(TMAppKeyset,
        related_name='user_keysets',
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    
    user_id = models.BigIntegerField(
        verbose_name="Twitter User ID",
        db_index=True,
        editable=False,
        blank=True,
        null=True)
    
    user_name = models.CharField(
        verbose_name="Twitter User Name",
        max_length=255,
        blank=True,
        null=True)
    
    class Meta:
        abstract = False
        order_with_respect_to = 'app_keyset'
        unique_together = (('key','secret'), ('user_name','app_keyset'))
        verbose_name = "Twitter User Keyset"
        verbose_name_plural = "Twitter User Keysets"
    
    def _get_credentials(self):
        from collections import defaultdict
        out = defaultdict(lambda: u'')
        if self.app_keyset:
            out.update(dict(
                consumer_key=self.app_keyset.key,
                consumer_secret=self.app_keyset.secret,
                access_token_key=self.key,
                access_token_secret=self.secret))
        return out
    
    credentials = property(_get_credentials)
    
    def _get_owner(self):
        if self.app_keyset:
            return self.app_keyset.owner
        return None
    
    owner = property(_get_owner)


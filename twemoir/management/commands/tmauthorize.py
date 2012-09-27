#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tmauthorize.py

Created by FI$H 2000 on 2011-08-02.
Copyright (c) 2011 Objects In Space And Time, LLC. All rights reserved.

"""
from django.core.management.base import BaseCommand
from optparse import make_option

from twemoir.models import TMTweet

tmauthorize_help = '''
    Authorizes a tweeter.
'''

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--open-browser', '-o', dest='open_browser', action='store_true',
            default=False,
            help="Automatically open the authorization URL.",
        ),
    )

    help = __doc__ = tmauthorize_help
    args = '[twitter user name] [-o/--open-browser]'

    can_import_settings = True
    requires_model_validation = True

    def handle(self, user=None, *args, **options):
        '''

        OAUTH ZUXXXXXXX!!!!!!

        This code is adapted from this:
        http://abhi74k.wordpress.com/2010/12/21/tweeting-from-python/

        '''
        from twemoir.models import TMAppKeyset, TMUserKeyset
        import oauth2 as oauth
        import sys, os, urlparse

        if not TMAppKeyset.objects.all().exists():
            out =   "No application keys in the database. "\
                    "Put one in using the admin interface. "
            print out
            sys.exit(1)

        if user is None:
            print "Specify a Twitter user to authorize."
            sys.exit(1)

        try:
            existent = TMUserKeyset.objects.get(user_name=user)
        except TMUserKeyset.DoesNotExist:
            print "Authorizing Twitter user: %s" % user
            print ""
        else:
            print "Twitter user %s is already authorized:"
            print "\t\t %20s\t %s" % ('User Key', existent.key)
            print "\t\t %20s\t %s" % ('User Secret', existent.secret)
            print "\t\t %20s\t %s" % ('App Key', existent.app_keyset.key)
            print "\t\t %20s\t %s" % ('App Secret', existent.app_keyset.secret)
            print ""
            sys.exit(0)

        print "Choose an App Keyset:"
        print ""

        str_tpl = "%4s %20s %30s %9s"
        default_appkey_id = TMAppKeyset.objects.all()[0].id
        print str_tpl % ('idx', 'Keyset Owner', 'Public Key', '#Auth')
        print str_tpl % ('-' * 4, '-' * 20, '-' * 30, '-' * 9)
        print ""
        for appkey in TMAppKeyset.objects.all():
            print str_tpl % (
                appkey.id,
                appkey.owner.get_full_name(),
                appkey.key,
                appkey.user_keysets.count())
        print ""

        while True:
            appkey_raw = raw_input('App Keyset ID [%s]: \t' % default_appkey_id).strip()
            try:
                appkey_id = appkey_raw and int(appkey_raw) or default_appkey_id
            except ValueError, err:
                print "*** Invalid app key: '%s'" % appkey_raw
                continue

            try:
                app_keyset = TMAppKeyset.objects.get(id=appkey_id)
            except TMAppKeyset.DoesNotExist:
                print "*** Couldn't find app key: '%s'" % appkey_raw
                continue

            if app_keyset:
                break

        CONSUMER_KEY = unicode(app_keyset.key)
        CONSUMER_SECRET = unicode(app_keyset.secret)
        request_token_url = 'https://api.twitter.com/oauth/request_token'
        access_token_url = 'https://api.twitter.com/oauth/access_token'
        authorize_url = 'https://api.twitter.com/oauth/authorize'

        print ""

        #print "CONSUMER KEY: %s" % CONSUMER_KEY
        #print "CONSUMER SECRET: %s" % CONSUMER_SECRET
        #print ""

        consumer = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
        client = oauth.Client(consumer)
        resp, content = client.request(request_token_url, "GET")

        request_token = dict(urlparse.parse_qsl(content))
        auth_url = "%s?oauth_token=%s" % (
            authorize_url, request_token['oauth_token'])

        print 'Please authorize: ' + auth_url

        if options.get('open_browser'):
            os.system('/usr/bin/open %s' % auth_url)

        verifier = raw_input('PIN: \t').strip()

        token = oauth.Token(
            request_token['oauth_token'], request_token['oauth_token_secret'])

        token.set_verifier(verifier)
        client = oauth.Client(consumer, token)

        resp, content = client.request(access_token_url, "POST")
        access_token = dict(urlparse.parse_qsl(content))

        #print "Access Token:"
        #print access_token.keys() # Save the output of the script which gives the access token
        #print access_token.values()
        #print "You may now access protected resources using the access tokens above."

        new_user_keyset = TMUserKeyset.objects.create(
            user_name=access_token['screen_name'],
            user_id=long(access_token['user_id']),
            app_keyset=app_keyset,
            key=access_token['oauth_token'],
            secret=access_token['oauth_token_secret'])

        new_user_keyset.save()

        print ""

        print "- ACCESS_KEY = '%s'" % access_token['oauth_token']
        print "- ACCESS_SECRET = '%s'" % access_token['oauth_token_secret']
        print "+ NEW KEYSET ID = '%s'" % new_user_keyset.id
        print ""


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tmsync.py

Created by FI$H 2000 on 2011-08-02.
Copyright (c) 2011 Objects In Space And Time, LLC. All rights reserved.

"""
from django.core.management.base import BaseCommand
from optparse import make_option

from twemoir.models import TMTweet

tmsync_help = '''
    Syncs tweets from the twemoir author's account (as defined
    in twemoir/credentials.py) into the local database,
    as TMTweet instances. Tweets that are already represented
    by local TMTweets will be updated.
    
    Options specific to this command:
    
        -A, --all       Get all of the twemoir author's
                        tweets, instead of only the latest
                        tweets not stored locally.
'''

class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('--all', '-A', dest='latest', action='store_false',
            default=True,
            help="Sync all tweets (instead of those after the latest in the database).",
        ),
    )
    
    help = __doc__ = tmsync_help
    args = '[user] [-A/--all]'
    
    can_import_settings = True
    requires_model_validation = True
    
    def handle(self, user=None, *args, **options):
        from twemoir.conf import settings
        
        if user is None:
            print "Syncing tweets from Twitter user '%s' (from twemoir.credentials) ..." % settings.AUTHOR_USER_NAME
            user = settings.AUTHOR_USER_NAME
        
        else:
            print "Syncing tweets from Twitter user '%s' (from CLI arguments) ..." % user
        
        if options.get('latest'):
            TMTweet.objects.sync_latest(user)
        
        else:
            TMTweet.objects.sync(user)


#!/usr/bin/env python
# encoding: utf-8
"""
twemoir/utils.py

Utilities used by twemoir for talking to Twitter.

Created by FI$H 2000 on 2012-01-22.
Copyright (c) 2012 Objects In Space And Time, LLC. All rights reserved.

"""
import sys, time, twitter
import re, htmlentitydefs

def TMPlayDead(**options):
    verbose = options.pop('verbose', False)
    api = twitter.Api(**options)
    
    try:
        sleep_time = api.MaximumHitFrequency()
    
    except twitter.TwitterError, err:
        if verbose:
            print >>sys.stderr, "ERROR: Twitter API -- %s" % (
                err,)
        sleep_time = 30
    
    if verbose:
        print >>sys.stderr, "Sleeping for %d seconds..." % (
            sleep_time,)
    
    time.sleep(sleep_time)
    return sleep_time


def TMUserStatusUpdate(tweet_text=u"", **options):
    """ Post a status update (a "tweet") to Twitter, as signified by
        the colloquial verb phrase "to tweet" as per typical employ.
        See Also: http://stackoverflow.com/a/4474362/298171 """
    verbose = options.pop('verbose', False)
    api = twitter.Api(**options)
    
    tweet = api.PostUpdate(tweet_text)
    
    # Sleep, as per the API's dictum.
    TMPlayDead(verbose=verbose, **options)
    return tweet


def TMUserTweets(user, **options):
    """ Get all tweets for a user.
        See Also: http://blogs.fluidinfo.com/terry/2009/06/24/python-code-for-retrieving-all-your-tweets/ """
    verbose = options.pop('verbose', False)
    since_id = options.pop('since_id', None)
    api = twitter.Api(**options)
    
    tweets = {}
    max_id = None
    total = 0
    
    while True:
        
        try:
            statuses = api.GetUserTimeline(user, count=200, include_entities=True,
                max_id=max_id, since_id=since_id)
        
        except twitter.TwitterError, err:
            if verbose:
                print >>sys.stderr, "ERROR: Twitter API -- %s" % (
                    err,)
            
            if 'capacity' in str(err).lower():
                continue
            else:
                return tweets.values()
        
        new_count = existent_count = 0
        
        for s in statuses:
            if s.id in tweets:
                existent_count += 1
            else:
                tweets[s.id] = s
                new_count += 1
        
        total += new_count
        
        if verbose:
            print >>sys.stderr, "Fetched %d/%d/%d new/old/total." % (
                new_count, existent_count, total)
        
        if new_count == 0:
            break
        
        max_id = min([s.id for s in statuses]) - 1
        
        # Sleep, as per the API's dictum.
        TMPlayDead(verbose=verbose, **options)
    
    return tweets.values()


def TMPreflightStruct(tweets, chapter_marker='>', paragraph_marker='-'):
    """ Arrange the data from an iterable of TMTweets (say, a list, or a queryset)
        into a set of nested dicts, as per the following:
    
        ~   » Hello, And Welcome To My Show.
        ~   Blah blah blah. 
        ~   ¶ Blah blah blah.
        ~   Blah blah blah.
        ~   Lorem ipsum. Si dolor amet.
        ~   ¶ Deus ex machina. Caveat Emptor.
        ~   ¶ Blah blah blah.
    
            ¶   Pilcrow             &#182; &para;       --> Starts a new paragraph.
            »   Right Angle-Quote   &#187; &raquo;      --> Starts and labels a chapter
    
        ================================================
    
        chapters[0]
        chapters[0]['title']                        = '' # always empty string for chapter 0
        chapters[0]['paragraphs']                   = [...]
        chapters[1]['title']                        = 'Something Titley'
        chapters[1]['paragraphs']                   = [...]
        chapters[1]['paragraphs'][0]
        chapters[1]['paragraphs'][0]['chunks']      = [...]
        """
    chapters = []
    chapters.append(dict(title='', paragraphs=[dict(chunks=[])]))
    ch = 0
    pr = 0
    ck = 0
    
    for tweet in tweets:
        txt = unicode(tweet.text).strip()
        
        if txt.startswith(chapter_marker):
            ch += 1
            pr = 0
            ck = 0
            chapters.append(dict(title=txt[1:], paragraphs=[dict(chunks=[])]))
        
        elif tweet.text.strip().startswith(paragraph_marker):
            pr += 1
            ck = 0
            chapters[ch]['paragraphs'].append(dict(chunks=[]))
        
        else:
            ck += 1
            chapters[ch]['paragraphs'][pr]['chunks'].append(txt)
    
    return chapters


def nonentitize(text):
    """ Removes HTML or XML character references and entities from a text string.
        See also: http://stackoverflow.com/q/57708/298171
        See also: http://effbot.org/zone/re-sub.htm#unescape-html """
    def fixup(m):
        text = m.group(0)
        
        if text[:2] == "&#": # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        
        elif text[:5] == "&nbsp":
            return " "
        
        else: # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        
        return text # leave as is
    
    return re.sub("&#?\w+;", fixup, text)



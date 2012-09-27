#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
twemoir/views.py

Created by FI$H 2000 on 2011-08-02.
Copyright (c) 2011 Objects In Space And Time, LLC. All rights reserved.

"""
from django.http import HttpResponse
from django.template import RequestContext, loader

from twemoir.models import TMTweet
from twemoir.forms import TMBoxForm
from twemoir.utils import TMPreflightStruct

CHAPTER_MARKER = u'»'
PARAGRAPH_MARKER = u'¶'

def paragraphs(request, option=None):
    """ Display the twemoir, using the paragraphs.html basic template. """
    tweets = TMTweet.objects.order_by('status_id')
    chapters = TMPreflightStruct(tweets,
        chapter_marker=CHAPTER_MARKER, paragraph_marker=PARAGRAPH_MARKER)
    form = TMBoxForm()
    
    if option in ('large',):
        template = 'twemoir/paralarge.html'
    else:
        template = 'twemoir/paragraphs.html'
    
    mt = loader.get_template(template)
    return HttpResponse(
        mt.render(
            RequestContext(
                request, {
                    'chapters': chapters,
                    'chapter_marker': CHAPTER_MARKER,
                    'paragraph_marker': PARAGRAPH_MARKER,
                    'form': form,
                }
            )
        )
    )


def bootstrap(request, user=None):
    """ Display the twemoir with a template based on Twitter's Bootstrap. """
    tweets = TMTweet.objects.order_by('status_id')
    chapters = TMPreflightStruct(tweets,
        chapter_marker=CHAPTER_MARKER, paragraph_marker=PARAGRAPH_MARKER)
    form = TMBoxForm()
    
    mt = loader.get_template('twemoir/bootstrap.html')
    return HttpResponse(
        mt.render(
            RequestContext(
                request, {
                    'chapters': chapters,
                    'chapter_marker': CHAPTER_MARKER,
                    'paragraph_marker': PARAGRAPH_MARKER,
                    'form': form,
                }
            )
        )
    )


def textbox(request, user=None):
    """ Display the twemoir with a template based on Twitter's Bootstrap. """
    tweets = TMTweet.objects.order_by('status_id')
    chapters = TMPreflightStruct(tweets,
        chapter_marker=CHAPTER_MARKER, paragraph_marker=PARAGRAPH_MARKER)
    form = TMBoxForm()

    mt = loader.get_template('twemoir/textbox.html')
    return HttpResponse(
        mt.render(
            RequestContext(
                request, {
                    'chapters': chapters,
                    'chapter_marker': CHAPTER_MARKER,
                    'paragraph_marker': PARAGRAPH_MARKER,
                    'form': form,
                }
            )
        )
    )



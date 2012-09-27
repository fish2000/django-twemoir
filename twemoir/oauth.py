#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
twemoir/oauth.py

Twitter views for OAuth2 API fucky-fuck.

Created by FI$H 2000 on 2011-08-02.
Copyright (c) 2011 Objects In Space And Time, LLC. All rights reserved.

"""
from django.http import HttpResponse
from django.template import Context, RequestContext, loader
from django.contrib.auth.decorators import login_required

#@login_required

def begin(request):
    return HttpResponse('YO DOGG')

def callback(request, authy_shit_and_such=None):
    return HttpResponse('YO DOGG')
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
twemoir/admin.py

Created by FI$H 2000 on 2011-08-02.
Copyright (c) 2011 Objects In Space And Time, LLC. All rights reserved.

"""

from django.contrib import admin
from docfield.modelfields import JSONField
import tagging.models as tags
import twemoir.models as tm
from twemoir.lib.adminfields.widgets import JsonPairInputs

class TMTweetHashtagFilter(admin.SimpleListFilter):
    title = u"Hashtag"
    parameter_name = 'hashtag'
    def __init__(self, request, params, model, model_admin):
        self.__model__ = model
        self.title = u"Hashtag (%s)" % len(list(tags.Tag.objects.usage_for_model(self.__model__)))
        super(TMTweetHashtagFilter, self).__init__(request, params, model, model_admin)
    
    def lookups(self, request, model_admin):
        tags = model_admin.queryset(request).tags()
        return [(str(t.name), u"#%s%s (%s)" % (
            t.name[:15],
            len(t.name) > 15 and u"…" or u"",
            t.items.count())) for t in sorted(tags,
                key=lambda t: t.items.count(), reverse=True)]
    def queryset(self, request, queryset):
        tagged = queryset.tagged(self.value())
        return tagged.count() > 0 and tagged or queryset.all()

class TMTweetAdmin(admin.ModelAdmin):
    ordering = ('status_id', 'id',)
    list_display = ('status_id','with_hashtags','text','user_id',)
    list_display_links = ('status_id',)
    list_filter = (TMTweetHashtagFilter,)
    
    search_fields = ['status_id','user_id','text','tweet_struct','_tags',]
    
    formfield_overrides = {
        JSONField: { 'widget': JsonPairInputs },
    }
    
    def with_hashtags(self, obj):
        return ', '.join([u"#%s" % t.name for t in obj.tags])
    with_hashtags.short_description = "Hashtags in Tweet"
    with_hashtags.allow_tags = True
    

admin.site.register(tm.TMTweet, TMTweetAdmin)
admin.site.register(tm.TMStagedTweet)
admin.site.register(tm.TMAppKeyset)
admin.site.register(tm.TMUserKeyset)
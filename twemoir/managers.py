
from django.db import models
from django.db.models.query import Q
from django.core.exceptions import ObjectDoesNotExist

import re
import tagging.models as tags
from delegate import delegate, DelegateManager

class TaggedQuerySet(models.query.QuerySet):
    
    count_re = re.compile(r'(select) (distinct) (.+) (count)(.*)(group by)(.+)(asc)$', flags=re.S|re.I|re.M)
    
    @delegate
    def tagged(self, name=None):
        """ Return a QuerySet of the model instances tagged with the named tag. """
        if name:
            try:
                t = tags.Tag.objects.filter(name=name).get()
            except ObjectDoesNotExist:
                return self.none()
            else:
                return self.filter(
                    id__in=t.items.get_by_model(self.model, t).values('id')
                )
        return self.none()
    
    @delegate
    def tags(self, related_to=None):
        """ Returns a QuerySet of tagging.models.Tag objects related to members of the QuerySet,
        optionally limited to those also related to the tag or tags named in related_to """
        if related_to is None:
            return tags.Tag.objects.filter(
                id__in=(t.id for t in tags.Tag.objects.usage_for_queryset(self.all()))
            )
        
        else:
            return tags.Tag.objects.filter(
                Q(id__in=(t.id for t in tags.Tag.objects.related_for_model(related_to, self.model))) &
                Q(id__in=(t.id for t in tags.Tag.objects.usage_for_queryset(self.all())))
            )
    
    @delegate
    def tagnames(self, related_to=None):
        """ Returns a list of the string names of all tags used by members of the QuerySet,
        optionally limited to those related to the tag or tags named in related_to """
        #return (t.name for t in tags.Tag.objects.usage_for_queryset(self.all()))
        return (t.name for t in self.tags(related_to=related_to))


class TaggedManager(DelegateManager):
    __queryset__ = TaggedQuerySet

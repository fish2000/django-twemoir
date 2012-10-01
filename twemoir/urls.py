
from django.conf.urls.defaults import patterns, url, include

app_patterns = patterns('',
    
    """
    url(r'^grafs/(?P<option>[\w\-]+)/?$',
        'twemoir.views.paragraphs',
        name="grafs_option"),
    """

)

# URL namespace
urlpatterns = patterns('',

    url(r'', include(app_patterns,
        namespace='twemoir', app_name='twemoir')),

)




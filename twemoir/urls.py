
from django.conf.urls.defaults import patterns, url, include

app_patterns = patterns('',

    url(r'^grafs/(?P<option>[\w\-]+)/?$',
        'twemoir.views.paragraphs',
        name="grafs_option"),

    url(r'^grafs/?$',
        'twemoir.views.paragraphs',
        name="grafs"),

    url(r'^/?$',
        'twemoir.views.paragraphs',
        name="root"),
)

# URL namespace
urlpatterns = patterns('',

    url(r'', include(app_patterns,
        namespace='twemoir', app_name='twemoir')),

)




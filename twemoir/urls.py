
from django.conf.urls.defaults import patterns, url, include

app_patterns = patterns('',

    url(r'^grafs/(?P<option>[\w\-]+)/?$',
        'twemoir.views.paragraphs',
        name="grafs_option"),

    url(r'^grafs/?$',
        'twemoir.views.paragraphs',
        name="grafs"),

    url(r'^bttstrp/?$',
        'twemoir.views.bootstrap',
        name="bttstrp"),

    url(r'^txtbxx/?$',
        'twemoir.views.textbox',
        name="txtbxx"),

    url(r'^/?$',
        'twemoir.views.paragraphs',
        name="root"),

    ####### >> HERE BE OAUTH2 DRAGONS << ########

    url(r'^auth/begin/?$',
        'twemoir.oauth.begin',
        name="auth-begin"),

    url(r'^auth/callback/?$',
        'twemoir.oauth.callback',
        name="auth-callback"),
)

# URL namespace
urlpatterns = patterns('',

    url(r'', include(app_patterns,
        namespace='twemoir', app_name='twemoir')),

)




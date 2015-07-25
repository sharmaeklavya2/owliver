from django.conf.urls import include, url, patterns
from django.contrib import admin

urlpatterns = [
	url(r'^admin/', include(admin.site.urls)),
	url(r'^accounts/', include('accounts.urls',namespace='accounts')),
	url(r'^', include('main.urls',namespace='main')),
]

from . import settings

if settings.DEBUG:
	urlpatterns+= patterns('django.views.static',
		(r'media/(?P<path>.*)','serve',{'document_root':settings.MEDIA_ROOT})
	)

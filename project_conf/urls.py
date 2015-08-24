from django.conf.urls import include, url, patterns
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
	url(r'^admin/', include(admin.site.urls)),
	url(r'^api/accounts/', include('accounts.api_urls',namespace='accounts_api')),
	url(r'^accounts/', include('accounts.urls',namespace='accounts')),
	url(r'^api/', include('main.api_urls',namespace='api')),
	url(r'^', include('main.urls',namespace='main')),
	url(r'^404/$', TemplateView.as_view(template_name='404.html')),
	url(r'^500/$', TemplateView.as_view(template_name='500.html')),
]

from . import settings

if settings.DEBUG:
	urlpatterns+= patterns('django.views.static',
		(r'media/(?P<path>.*)','serve',{'document_root':settings.MEDIA_ROOT})
	)

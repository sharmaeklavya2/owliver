from django.conf.urls import url
from . import api_views

urlpatterns = [
	url(r'^login/$', api_views.login_view, name='login'),
	url(r'^logout/$', api_views.logout_view, name='logout'),

	url(r'^account_info/$', api_views.account_info, name='account_info'),
#	url(r'^users/$', api_views.user_list, name='user_list'),
#	url(r'^users/()/$', api_views.user, name='user'),
]

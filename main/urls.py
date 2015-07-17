from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^about/$', views.about, name='about'),
	url(r'^attempt_ques/(?P<aid>[0-9]+)/$', views.attempt_question, name='attempt_question'),
	url(r'^submit/(?P<aid>[0-9]+)/$', views.submit, name='submit'),
]

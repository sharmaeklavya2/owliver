from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^about/$', views.about, name='about'),
	url(r'^eas_list/$', views.eas_list, name='eas_list'),
	url(r'^attempt_exam/(?P<eid>[0-9]+)/$', views.attempt_exam, name='attempt_exam'),
	url(r'^attempt_section/(?P<sid>[0-9]+)/$', views.attempt_section, name='attempt_section'),
	url(r'^attempt_ques/(?P<aid>[0-9]+)/$', views.attempt_question, name='attempt_question'),
	url(r'^submit/(?P<aid>[0-9]+)/$', views.submit, name='submit'),
]

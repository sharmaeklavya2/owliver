from django.conf.urls import url
from . import views

urlpatterns = [
	# about and index
	url(r'^$', views.index, name='index'),
	url(r'^about/$', views.about, name='about'),

	# viewing and manipulating exam lists
	url(r'^public_exams/$', views.public_exam_list, name='public_exam_list'),
	url(r'^user_list/$', views.user_list, name='user_list'),
	url(r'^user_exams/(?P<username>\w+)/$', views.user_exam_list, name='user_exam_list'),
	url(r'^eas_list/$', views.eas_list, name='eas_list'),
	url(r'^exam_cover/(?P<eid>[0-9]+)/$', views.exam_cover, name='exam_cover'),
	url(r'^make_eas/(?P<eid>[0-9]+)/$', views.make_eas, name='make_eas'),
	url(r'^start_eas/(?P<eid>[0-9]+)/$', views.start_eas, name='start_eas'),
	url(r'^disown_exam/(?P<eid>[0-9]+)/$', views.disown_exam, name='disown_exam'),

	# attempting an exam
	url(r'^eas_cover/(?P<eid>[0-9]+)/$', views.eas_cover, name='eas_cover'),
	url(r'^sas_cover/(?P<sid>[0-9]+)/$', views.sas_cover, name='sas_cover'),
	url(r'^answer/(?P<aid>[0-9]+)/$', views.answer_view, name='answer'),
	url(r'^submit/(?P<aid>[0-9]+)/$', views.submit, name='submit'),
	url(r'^submit_eas/(?P<eid>[0-9]+)/$', views.submit_eas, name='submit_eas'),
]

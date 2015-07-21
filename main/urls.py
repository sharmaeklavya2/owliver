from django.conf.urls import url
from . import views

urlpatterns = [
	# about and index
	url(r'^$', views.index, name='index'),
	url(r'^about/$', views.about, name='about'),

	# viewing and manipulating exam lists
	url(r'^public_exams/$', views.public_exam_list, name='public_exam_list'),
	url(r'^user_exams/$', views.my_exam_list, name='my_exam_list'),
	url(r'^eas_list/$', views.eas_list, name='eas_list'),
	url(r'^exam_cover/(?P<eid>[0-9]+)/$', views.exam_cover, name='exam_cover'),
	url(r'^add_eas/(?P<eid>[0-9]+)/$', views.add_eas, name='add_eas'),
	url(r'^start_eas/(?P<eid>[0-9]+)/$', views.start_eas, name='start_eas'),

	# attempting an exam
	url(r'^attempt_exam/(?P<eid>[0-9]+)/$', views.attempt_exam, name='attempt_exam'),
	url(r'^attempt_section/(?P<sid>[0-9]+)/$', views.attempt_section, name='attempt_section'),
	url(r'^attempt_ques/(?P<aid>[0-9]+)/$', views.attempt_question, name='attempt_question'),
	url(r'^submit/(?P<aid>[0-9]+)/$', views.submit, name='submit'),
	url(r'^submit_exam/(?P<eid>[0-9]+)/$', views.submit_exam, name='submit_exam'),
]

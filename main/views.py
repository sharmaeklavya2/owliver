from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from main import models
from main.models import Answer, ExamAnswerSheet, SectionAnswerSheet, McqAnswerToMcqOption
from custom_exceptions import CustomException, QuestionTypeNotImplemented

import django
import sys

def get_python_version():
	return ".".join([str(sys.version_info.major),str(sys.version_info.minor)])
def get_django_version():
	return django.get_version()[:4]

def about(request):
	context_dict = {}
	context_dict["python_version"] = get_python_version()
	context_dict["django_version"] = get_django_version()
	context_dict["contributors"] = ["Eklavya Sharma"]
	return render(request,"about.html",context_dict)

def index(request):
	context_dict = {}
	return render(request,"index.html",context_dict)

class ParaayaAnswer(CustomException):
	# In hindi, paraaya means "something/someone which does not belong to you/us"
	def __str__(self):
		return "This link does not belong to you"
class ExamNotStarted(CustomException):
	def __str__(self):
		return "This exam has not begun"
class InvalidFormData(CustomException):
	def __str__(self):
		return "This form has invalid POST data. Either there is a bug in our code or some hacker is at work."

# Attempt ==========================================================================================

@login_required
def eas_list(request):
	context_dict = {"eas_list":request.user.examanswersheet_set.all()}
	return render(request,"attempt/eas_list.html",context_dict)

@login_required
def attempt_exam(request,eid):
	eid = int(eid)
	eas = get_object_or_404(ExamAnswerSheet, id=eid)
	context_dict = {"eas":eas}
	exam = eas.exam
	context_dict["eas"]=eas
	context_dict["exam"]=exam
	return render(request,"attempt/exam.html",context_dict)

@login_required
def attempt_section(request,sid):
	sid = int(sid)
	sas = get_object_or_404(SectionAnswerSheet, id=sid)
	context_dict = {"sas":sas}
	eas = sas.exam_answer_sheet
	section = sas.section
	exam = eas.exam
	context_dict["eas"]=eas
	context_dict["exam"]=exam
	context_dict["section"]=section
	return render(request,"attempt/section.html",context_dict)

def fill_context_dict_using_answer(current_user,answer):
	context_dict = {"answer":answer}
	sas = answer.section_answer_sheet
	eas = sas.exam_answer_sheet
# These lines have been commented out for debugging purposes
#	if eas.user.username != current_user.username:
#		raise ParaayaAnswer()
#	if eas.get_timer_status()!=ExamAnswerSheet.TIMER_IN_USE:
#		raise ExamNotStarted()
	section = sas.section
	exam = section.exam
	special_question = answer.get_typed_question()
	special_answer = answer.get_special_answer()
	question = special_question.question

	qset = sas.answer_set.filter(id__lt=answer.id)
	qno = qset.count()+1
	context_dict["qno"] = qno
	if qno>1:
		context_dict["prevaid"] = qset.last().id
	else:
		context_dict["prevaid"] = None
	qset = sas.answer_set.filter(id__gt=answer.id)
	if qset.count()>0:
		context_dict["nextaid"] = qset.first().id
	else:
		context_dict["nextaid"] = None

	context_dict["qtype"] = special_question.get_qtype()
	context_dict["sas"] = sas
	context_dict["eas"] = eas
	context_dict["section"] = section
	context_dict["exam"] = exam
	context_dict["question"] = question
	context_dict["special_question"] = special_question
	context_dict["answer"] = answer
	context_dict["special_answer"] = special_answer
	return context_dict

@login_required
def attempt_question(request,aid):
	aid = int(aid)
	answer = get_object_or_404(Answer, id=aid)
	try:
		context_dict = fill_context_dict_using_answer(request.user,answer)
		return render(request, "attempt/"+context_dict["qtype"]+"_question.html", context_dict)
	except (ParaayaAnswer,ExamNotStarted) as cexp:
		context_dict = {"base_body":str(cexp)}
		return render(request, "base.html", context_dict)

@login_required
def submit(request,aid):
	if request.method!="POST":
		raise Http404("This page cannot be accessed via GET")

	aid = int(aid)
	answer = get_object_or_404(Answer, id=aid)
	context_dict = fill_context_dict_using_answer(request.user,answer)

	# save response to database
	qtype = context_dict["qtype"]
	special_answer = context_dict["special_answer"]
	if qtype=="text":
		if "response" not in request.POST:
			raise InvalidFormData()
		special_answer.response=request.POST["response"]
	elif qtype=="mcq":
		special_answer.chosen_options.clear()
		chosen_option_ids = request.POST.getlist("response")
		for option_id in chosen_option_ids:
			link = McqAnswerToMcqOption(mcq_answer=special_answer,mcq_option_id=option_id)
			link.save()
	else:
		raise QuestionTypeNotImplemented(qtype)
	special_answer.save()

	# redirect
	if "submit" in request.POST:
		nextaid = aid
	elif "submit_and_next" in request.POST:
		nextaid = context_dict["nextaid"]
	else:
		raise InvalidFormData()
	return HttpResponseRedirect(reverse("main:attempt_question",args=(nextaid,)))

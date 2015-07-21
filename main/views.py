from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from main import models
from main.models import Exam, Answer, ExamAnswerSheet, SectionAnswerSheet, McqAnswerToMcqOption
from custom_exceptions import CustomException, QuestionTypeNotImplemented
from scripts import add_anssheet

import sys
import django
from datetime import timedelta, datetime
from django.utils import timezone

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
class ExamEnded(CustomException):
	def __str__(self):
		return "This exam has ended"
class InvalidFormData(CustomException):
	def __str__(self):
		return "This form has invalid POST data. Either there is a bug in our code or some hacker is at work."

# Exam Lists =======================================================================================

def public_exam_list(request):
	context_dict = {"exam_list":Exam.objects.filter(owner__isnull=True)}
	context_dict["base_title"] = "Owliver - Public Exams"
	context_dict["base_h1"] = "Public Exams"
	return render(request,"exam_list.html",context_dict)

@login_required
def my_exam_list(request):
	context_dict = {"exam_list":Exam.objects.filter(owner=request.user)}
	context_dict["base_title"] = "Owliver - My Exams"
	context_dict["base_h1"] = "Exams owned by me"
	return render(request,"exam_list.html",context_dict)

@login_required
def eas_list(request):
	context_dict = {"eas_list":request.user.examanswersheet_set.all()}
	return render(request,"eas_list.html",context_dict)

def exam_cover(request,eid):
	exam = get_object_or_404(Exam,id=eid)
	context_dict = {"exam":exam}
	if exam.time_limit == timedelta(0):
		context_dict["infinite_time"] = True
	if request.user.is_authenticated():
		context_dict["can_attempt"] = exam.can_attempt(request.user)
	return render(request,"exam_cover.html",context_dict)

@login_required
def add_eas(request,eid):
	if request.method!="POST":
		raise Http404("This page is only accessible via POST")
	exam = get_object_or_404(Exam,id=eid)
	if exam.can_attempt(request.user):
		eas = add_anssheet.add_eas(exam,request.user)
		if "start" in request.POST:
			eas.set_timer()
		return HttpResponseRedirect(reverse("main:eas_list"))
	else:
		context_dict = {"base_body":"You do not have permission to attempt this exam."}
		return render(request, "base.html", context_dict)

@login_required
def start_eas(request,eid):
	if request.method!="POST":
		raise Http404("This page is only accessible via POST")
	eas = get_object_or_404(ExamAnswerSheet,id=eid)
	if eas.user!=request.user:
		raise Http404(str(ParaayaAnswer()))
	if eas.get_timer_status() == ExamAnswerSheet.TIMER_NOT_SET:
		eas.set_timer()
	return HttpResponseRedirect(reverse("main:attempt_exam",args=(eas.id,)))

# Attempt ==========================================================================================

def verify_user_permission(eas,current_user):
	# check if a user is allowed to look at a page
	if eas.user.username != current_user.username:
		raise ParaayaAnswer()
	timer_status = eas.get_timer_status()
	if timer_status==ExamAnswerSheet.TIMER_ENDED:
		raise ExamEnded()
	if timer_status!=ExamAnswerSheet.TIMER_IN_PROGRESS:
		raise ExamNotStarted()

def get_dict_with_eas_values(eas,current_user):
	context_dict = {"eas":eas}
	timer_status = eas.get_timer_status()
	context_dict["timer_status"] = timer_status
	context_dict["TIMER_ERROR"] = ExamAnswerSheet.TIMER_IN_PROGRESS
	context_dict["TIMER_NOT_SET"] = ExamAnswerSheet.TIMER_NOT_SET
	context_dict["TIMER_NOT_STARTED"] = ExamAnswerSheet.TIMER_NOT_STARTED
	context_dict["TIMER_IN_PROGRESS"] = ExamAnswerSheet.TIMER_IN_PROGRESS
	context_dict["TIMER_ENDED"] = ExamAnswerSheet.TIMER_ENDED
	if timer_status==ExamAnswerSheet.TIMER_IN_PROGRESS:
		now = timezone.now()
		context_dict["elapsed_time"] = now - eas.start_time
		if eas.end_time!=None:
			context_dict["remaining_time"] = eas.end_time() - now
	exam = eas.exam
	context_dict["exam"] = exam
	context_dict["can_view_solutions"] = (exam.can_view_solutions(current_user) and timer_status==ExamAnswerSheet.TIMER_ENDED)
	return context_dict

@login_required
def attempt_exam(request,eid):
	eid = int(eid)
	eas = get_object_or_404(ExamAnswerSheet, id=eid)
	try:
		verify_user_permission(eas,request.user)
	except ParaayaAnswer as paexp:
		context_dict = {"base_body":str(paexp)}
		return render(request, "base.html", context_dict)
	except (ExamNotStarted,ExamEnded):
		pass
	context_dict = get_dict_with_eas_values(eas,request.user)
	exam = context_dict["exam"]
	timer_status = context_dict["timer_status"]

	# Generate stats for result card
	sas_set = list(eas.sectionanswersheet_set.all())
	context_dict["sas_set"] = sas_set
	eas.corr=0; eas.wrong=0; eas.att=0; eas.na=0;
	eas.hints=0; eas.marks=0; eas.tot=0;
	hint_col = False
	for sas in sas_set:
		if sas.section.allowed_attempts==0 and timer_status!=ExamAnswerSheet.TIMER_ENDED:
			sas.att, sas.na, sas.hints = sas.attempt_freq()
			sas.corr = ""; sas.wrong = ""; sas.marks = "";
		else:
			sas.corr, sas.wrong, sas.na, sas.hints, sas.marks = sas.result_freq()
			sas.att = sas.corr + sas.wrong
		if sas.section.hint_deduction>0:
			hint_col = True
		sas.tot = sas.na + sas.att
		attrs = ("corr","wrong","marks")
		for attr in attrs:
			if getattr(eas,attr)!="" and getattr(sas,attr)!="":
				setattr(eas,attr,getattr(eas,attr)+getattr(sas,attr))
			else:
				setattr(eas,attr,"")
		attrs = ("att","na","hints","tot")
		for attr in attrs:
			setattr(eas,attr,getattr(eas,attr)+getattr(sas,attr))
		context_dict["hint_col"] = hint_col
	return render(request,"attempt/exam.html",context_dict)

def get_dict_with_sas_values(sas,current_user):
	eas = sas.exam_answer_sheet
	context_dict = get_dict_with_eas_values(eas,current_user)
	context_dict["sas"] = sas
	context_dict["section"] = sas.section

	qset = eas.sectionanswersheet_set.filter(id__lt=sas.id)
	# qset means queryset
	sasno = qset.count()+1
	context_dict["sasno"] = sasno
	# Check next and prev questions in same section
	if sasno>1:
		prevsid = qset.last().id
		context_dict["prevsecname"] = SectionAnswerSheet.objects.get(id=prevsid).section.name
	else:
		prevsid = None
	qset = eas.sectionanswersheet_set.filter(id__gt=sas.id)
	if qset.exists():
		nextsid = qset.first().id
		context_dict["nextsecname"] = SectionAnswerSheet.objects.get(id=nextsid).section.name
	else:
		nextsid = None

	context_dict["prevsid"] = prevsid
	context_dict["nextsid"] = nextsid
	return context_dict

@login_required
def attempt_section(request,sid):
	sid = int(sid)
	sas = get_object_or_404(SectionAnswerSheet, id=sid)
	sas.corr, sas.wrong, sas.na, sas.hints, sas.marks = sas.result_freq()
	context_dict = get_dict_with_sas_values(sas,request.user)
	try:
		verify_user_permission(context_dict["eas"],request.user)
	except (ParaayaAnswer,ExamNotStarted) as cexp:
		context_dict = {"base_body":str(cexp)}
		return render(request, "base.html", context_dict)
	except ExamEnded:
		pass
	return render(request,"attempt/section.html",context_dict)

def get_dict_with_answer_values(answer,current_user):
	sas = answer.section_answer_sheet
	context_dict = get_dict_with_sas_values(sas,current_user)
	context_dict["answer"] = answer
	special_question = answer.get_typed_question()
	special_answer = answer.get_special_answer()
	question = special_question.question

	prevsid = context_dict["prevsid"]
	nextsid = context_dict["nextsid"]

	qset = sas.answer_set.filter(id__lt=answer.id)
	# qset means queryset, qno means question number
	qno = qset.count()+1
	context_dict["qno"] = qno
	# Check next and prev questions in same section
	if qno>1:
		prevaid = qset.last().id
	else:
		prevaid = None
	qset = sas.answer_set.filter(id__gt=answer.id)
	if qset.exists():
		nextaid = qset.first().id
	else:
		nextaid = None

#	# Check next and previous questions in different sections if not found in same section
#	if prevaid==None and prevsid!=None:
#		prevaid = SectionAnswerSheet.objects.get(id=prevsid).answer_set.last().id
#	if nextaid==None and nextsid!=None:
#		nextaid = SectionAnswerSheet.objects.get(id=nextsid).answer_set.first().id

	context_dict["prevaid"] = prevaid
	context_dict["nextaid"] = nextaid
	context_dict["qtype"] = special_question.get_qtype()
	context_dict["question"] = question
	context_dict["special_question"] = special_question
	context_dict["answer"] = answer
	context_dict["special_answer"] = special_answer
	return context_dict

@login_required
def attempt_question(request,aid):
	aid = int(aid)
	answer = get_object_or_404(Answer, id=aid)
	context_dict = get_dict_with_answer_values(answer,request.user)
	try:
		verify_user_permission(context_dict["eas"],request.user)
	except (ParaayaAnswer,ExamNotStarted,ExamEnded) as cexp:
		context_dict = {"base_body":str(cexp)}
		return render(request, "base.html", context_dict)
	return render(request,"attempt/"+context_dict["qtype"]+"_question.html",context_dict)

@login_required
def submit(request,aid):
	if request.method!="POST":
		raise Http404("This page is only accessible via POST")

	aid = int(aid)
	answer = get_object_or_404(Answer, id=aid)
	context_dict = get_dict_with_answer_values(answer,request.user)
	eas = context_dict["eas"]
	try:
		verify_user_permission(eas,request.user)
	except (ParaayaAnswer,ExamNotStarted,ExamEnded) as cexp:
		context_dict = {"base_body":str(cexp)}
		return render(request, "base.html", context_dict)

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
	if not nextaid:
		nextaid = aid
	return HttpResponseRedirect(reverse("main:attempt_question",args=(nextaid,)))

@login_required
def submit_exam(request,eid):
	if request.method!="POST":
		raise Http404("This page is only accessible via POST")
	eas = get_object_or_404(ExamAnswerSheet,id=eid)
	if eas.user!=request.user:
		raise Http404(str(ParaayaAnswer()))
	timer_status = eas.get_timer_status()
	if timer_status == ExamAnswerSheet.TIMER_IN_PROGRESS:
		eas.end_time = timezone.now()
		eas.save()
	elif timer_status == ExamAnswerSheet.TIMER_NOT_STARTED:
		eas.end_time = eas.start_time
		eas.save()
	return HttpResponseRedirect(reverse("main:attempt_exam",args=(eas.id,)))

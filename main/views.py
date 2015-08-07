from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from main import models
from main.models import Exam, Answer, ExamAnswerSheet, SectionAnswerSheet, McqAnswerToMcqOption
from custom_exceptions import CustomException, QuestionTypeNotImplemented
from scripts import add_anssheet, load_unicode

EAS = ExamAnswerSheet

import sys
import django
import os
from datetime import timedelta, datetime
from django.utils import timezone

def get_python_version():
	return ".".join([str(sys.version_info.major),str(sys.version_info.minor)])
def get_django_version():
	return django.get_version()[:4]
#	return django.get_version()

def about(request):
	context_dict = {}
	context_dict["python_version"] = get_python_version()
	context_dict["django_version"] = get_django_version()
	authors_list = []
	authors_file = open(os.path.join(settings.BASE_DIR,"AUTHORS.txt"))
	for line in authors_file:
		authors_list.append(line.strip())
	authors_file.close()
	context_dict["contributors"] = authors_list
	return render(request,"about.html",context_dict)

def index(request):
	return render(request,"index.html",{})

def instructions(request):
	return render(request,"instructions.html",{})

exam_not_started_str = "This exam has not begun"
exam_ended_str = "This exam has ended"

class InvalidUser(CustomException):
	exp_str = "This link does not belong to you"
	def __str__(self):
		return InvalidUser.exp_str
class InvalidFormData(CustomException):
	exp_str = "This form has invalid POST data. Either there is a bug in our code or some hacker is at work."
	def __str__(self):
		return InvalidFormData.exp_str

def base_response(request,body,title=None,h1=None):
	context_dict = {"base_body":body}
	if title:
		context_dict["base_title"] = title
	if h1:
		context_dict["base_h1"] = h1
	return render(request, "base.html", context_dict)

# Exam Lists =======================================================================================

def public_exam_list(request):
	context_dict = {"exam_list":Exam.objects.filter(owner__isnull=True)}
	context_dict["base_title"] = settings.PROJECT_NAME+" - Public Exams"
	context_dict["base_h1"] = "Public Exams"
	return render(request,"exam_list.html",context_dict)

def user_list(request):
	user_list = list(User.objects.filter(exam__isnull=False))
	context_dict = {"user_list": user_list}
	print(user_list)
	return render(request,"user_list.html",context_dict)

def user_exam_list(request,username):
	user = get_object_or_404(User,username=username)
	context_dict = {"exam_list":Exam.objects.filter(owner=user)}
	context_dict["base_title"] = settings.PROJECT_NAME+" - {username}'s Exams".format(username=username)
	context_dict["base_h1"] = "Exams owned by "+username
	return render(request,"exam_list.html",context_dict)

@login_required
def eas_list(request):
	eas_list = list(request.user.examanswersheet_set.all())
	context_dict = {"eas_exist": len(eas_list)>0}
	in_progress_list = []
	not_started_list = []
	ended_list = []
	for eas in eas_list:
		timer_status = eas.get_timer_status()
		if timer_status == EAS.TIMER_IN_PROGRESS:
			in_progress_list.append(eas)
		elif timer_status == EAS.TIMER_NOT_SET or timer_status == EAS.TIMER_NOT_STARTED:
			not_started_list.append(eas)
		elif timer_status == EAS.TIMER_ENDED:
			ended_list.append(eas)
	context_dict["in_progress_list"] = in_progress_list
	context_dict["not_started_list"] = not_started_list
	context_dict["ended_list"] = ended_list
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
def disown_exam(request,eid):
	if request.method!="POST":
		raise Http404("This page is only accessible via POST")
	exam = get_object_or_404(Exam,id=eid)
	if exam.owner != request.user:
		return base_response(request,InvalidUser.exp_str)
	exam.owner = None
	exam.attempt_group = None
	exam.solutions_group = None
	exam.can_attempt_again = True
	exam.save()
	return HttpResponseRedirect(reverse('main:exam_cover',args=(eid,)))

@login_required
def make_eas(request,eid):
	if request.method!="POST":
		raise Http404("This page is only accessible via POST")
	exam = get_object_or_404(Exam,id=eid)
	if exam.can_attempt(request.user):
		eas = add_anssheet.add_eas(exam,request.user)
		if "start" in request.POST:
			eas.set_timer()
		return HttpResponseRedirect(reverse("main:eas_cover",args=(eas.id,)))
	else:
		return base_response(request, "You do not have permission to attempt this exam.")

@login_required
def start_eas(request,eid):
	if request.method!="POST":
		raise Http404("This page is only accessible via POST")
	eas = get_object_or_404(ExamAnswerSheet,id=eid)
	if eas.user!=request.user:
		raise Http404(str(ParaayaAnswer()))
	if eas.get_timer_status() == EAS.TIMER_NOT_SET:
		eas.set_timer()
	return HttpResponseRedirect(reverse("main:eas_cover",args=(eas.id,)))

# Attempt ==========================================================================================

def exam_not_started(timer_status):
	return timer_status!=EAS.TIMER_IN_PROGRESS and timer_status!=EAS.TIMER_ENDED

def get_dict_with_eas_values(eas,current_user):
	if eas.user!=current_user:
		raise InvalidUser()
	context_dict = {"eas":eas}
	timer_status = eas.get_timer_status()
	context_dict["timer_status"] = timer_status
	context_dict["EAS"] = EAS
	result_freq = eas.result_freq()
	context_dict["questions_attempted"] = result_freq[0]+result_freq[1]
	context_dict["actual_marks"] = result_freq[4]
	if timer_status==EAS.TIMER_IN_PROGRESS:
		now = timezone.now()
		context_dict["elapsed_time"] = now - eas.start_time
		if eas.end_time!=None:
			context_dict["remaining_time"] = eas.end_time - now
	exam = eas.exam
	context_dict["exam"] = exam
	context_dict["score_visible"] = not exam.section_set.filter(allowed_attempts=0).exists()
	context_dict["can_view_solutions"] = (exam.can_view_solutions(current_user) and timer_status==EAS.TIMER_ENDED)
	return context_dict

@login_required
def eas_cover(request,eid):
	eid = int(eid)
	eas = get_object_or_404(ExamAnswerSheet, id=eid)
	try:
		context_dict = get_dict_with_eas_values(eas,request.user)
	except InvalidUser:
		return base_response(request, InvalidUser.exp_str)
	exam = context_dict["exam"]
	timer_status = context_dict["timer_status"]
	context_dict["show_end_button"] = timer_status==EAS.TIMER_IN_PROGRESS or (timer_status==EAS.TIMER_NOT_STARTED and eas.start_time!=eas.end_time) 

	# Generate stats for result card
	if timer_status == EAS.TIMER_ENDED or timer_status == EAS.TIMER_IN_PROGRESS:
		sas_set = list(eas.sectionanswersheet_set.all())
		context_dict["sas_set"] = sas_set
		eas.corr=0; eas.wrong=0; eas.att=0; eas.na=0;
		eas.hints=0; eas.marks=0; eas.tot=0; eas.max_marks=0;
		hint_col = False
		for sas in sas_set:
			show_results = (sas.section.allowed_attempts!=0 or timer_status==EAS.TIMER_ENDED)
			if show_results:
				sas.corr, sas.wrong, sas.na, sas.hints, sas.marks = sas.result_freq()
				sas.att = sas.corr + sas.wrong
			else:
				sas.att, sas.na, sas.hints = sas.attempt_freq()
				sas.corr = ""; sas.wrong = ""; sas.marks = "";
			sas.tot = sas.na + sas.att
			sas.max_marks = sas.section.max_marks()
			if show_results:
				sas.perc = 100*sas.marks/sas.max_marks
			else:
				sas.perc = ""
			if sas.section.hint_deduction>0:
				hint_col = True
			attrs = ("corr","wrong","marks")
			for attr in attrs:
				if getattr(eas,attr)!="" and getattr(sas,attr)!="":
					setattr(eas,attr,getattr(eas,attr)+getattr(sas,attr))
				else:
					setattr(eas,attr,"")
			attrs = ("att","na","hints","tot","max_marks")
			for attr in attrs:
				setattr(eas,attr,getattr(eas,attr)+getattr(sas,attr))
		if eas.marks!="":
			eas.perc = 100*eas.marks/eas.max_marks
		else:
			eas.perc = ""
		context_dict["hint_col"] = hint_col
	return render(request,"eas_cover.html",context_dict)

def fill_dict_with_sas_values(context_dict,sas):
	context_dict["sas"] = sas
	section = sas.section
	context_dict["section"] = section
	eas = sas.exam_answer_sheet

	actual_marks = context_dict["actual_marks"]
	questions_attempted = context_dict["questions_attempted"]
	timer_status = context_dict["timer_status"]
	context_dict["unlocked"] = timer_status==EAS.TIMER_ENDED or section.is_unlocked(actual_marks, questions_attempted)

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

def get_result_str_and_marks(section,result,viewed_hint,cstr="Correct",wstr="Wrong",nastr="Not attempted"):
	if result==True:
		result_str = cstr
		marks = section.correct_marks
	elif result==False:
		result_str = wstr
		marks = section.wrong_marks
	else:
		result_str = nastr
		marks = section.na_marks
	if viewed_hint:
		marks-= section.hint_deduction
	return (result_str,marks)

@login_required
def sas_cover(request,sid):
	sid = int(sid)
	sas = get_object_or_404(SectionAnswerSheet, id=sid)
	section = sas.section
	eas = sas.exam_answer_sheet
	try:
		context_dict = get_dict_with_eas_values(eas,request.user)
	except InvalidUser:
		return base_response(request, InvalidUser.exp_str)
	if exam_not_started(context_dict["timer_status"]):
		return base_response(request, exam_not_started_str)

	context_dict["hint_col"] = section.hint_deduction > 0
	timer_status = context_dict["timer_status"]
	show_results = (sas.section.allowed_attempts!=0 or timer_status==EAS.TIMER_ENDED)
	context_dict["show_results"] = show_results

	max_marks = section.max_marks()
	context_dict["max_marks"] = max_marks
	if show_results:
		sas.corr, sas.wrong, sas.na, sas.hints, sas.marks = sas.result_freq()
		sas.att = sas.corr + sas.wrong
		sas.perc = 100*sas.marks/max_marks
	else:
		sas.att, sas.na, sas.hints = sas.attempt_freq()
	sas.tot = sas.att + sas.na
	answer_list = list(sas.answer_set.all())
	for answer in answer_list:
		answer.is_attable = answer.is_attemptable()
		answer.marks=""
		if show_results:
			result = answer.result()
			answer.res = result
			answer.result_str,answer.marks = get_result_str_and_marks(section,result,answer.viewed_hint,nastr="NA")
			answer.is_att = result!=None
		else:
			answer.is_att = answer.is_attempted()
			if answer.is_att:
				answer.result_str = "Attempted"
			else:
				answer.result_str = "NA"
	context_dict["answer_list"] = answer_list
	fill_dict_with_sas_values(context_dict, sas)
	context_dict["unicode_dict"] = load_unicode.unicode_dict
	return render(request,"sas_cover.html",context_dict)

def fill_dict_with_answer_values(context_dict,answer,verbose=False):
	context_dict["answer"] = answer
	sas = answer.section_answer_sheet
	special_question = answer.get_typed_question()
	special_answer = answer.get_special_answer()
	question = special_question.question
	context_dict["is_attable"] = answer.is_attemptable()
	context_dict["is_attable2"] = answer.is_attemptable2()

	if verbose:
		result = special_answer.result()
		returned_tuple = get_result_str_and_marks(sas.section,result,answer.viewed_hint)
		context_dict["result_str"],context_dict["marks"] = returned_tuple

	all_att = sas.section.allowed_attempts
	if all_att<=0:
		context_dict["remaining_attempts"] = ""
	else:
		context_dict["remaining_attempts"] = all_att-answer.attempts

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

@login_required
def answer_view(request,aid):
	aid = int(aid)
	answer = get_object_or_404(Answer, id=aid)
	sas = answer.section_answer_sheet
	eas = sas.exam_answer_sheet
	try:
		context_dict = get_dict_with_eas_values(eas,request.user)
	except InvalidUser:
		return base_response(request, InvalidUser.exp_str)
	timer_status = context_dict["timer_status"]
	if exam_not_started(timer_status):
		return base_response(request, exam_not_started_str)
	fill_dict_with_sas_values(context_dict,sas)
	unlocked = context_dict["unlocked"]
	if not unlocked:
		return base_response(request,"This section is locked")

	fill_dict_with_answer_values(context_dict,answer,verbose=True)
	if timer_status==EAS.TIMER_IN_PROGRESS and context_dict["is_attable"]:
		folder="attempt"
	else:
		folder="review"

	qtype = context_dict["qtype"]
	special_answer = context_dict["special_answer"]
	special_question = context_dict["special_question"]
	context_dict["show_correct_answer"] = (timer_status==EAS.TIMER_ENDED or not context_dict["is_attable"])
	if qtype=="text":
		if special_question.ignore_case:
			context_dict["case_sens"] = "No"
		else:
			context_dict["case_sens"] = "Yes"
	elif qtype=="mcq":
		option_list = list(special_question.mcqoption_set.all())
		chosen_options = set(special_answer.chosen_options.all())
		for option in option_list:
			option.is_chosen = (option in chosen_options)
		context_dict["option_list"] = option_list
	else:
		raise QuestionTypeNotImplemented(qtype)
	context_dict["unicode_dict"] = load_unicode.unicode_dict
	return render(request, os.path.join(folder,context_dict["qtype"]+"_question.html"), context_dict)

@login_required
def submit(request,aid):
	if request.method!="POST":
		raise Http404("This page is only accessible via POST")

	aid = int(aid)
	answer = get_object_or_404(Answer, id=aid)
	sas = answer.section_answer_sheet
	eas = sas.exam_answer_sheet
	try:
		context_dict = get_dict_with_eas_values(eas,request.user)
	except InvalidUser:
		return base_response(request, InvalidUser.exp_str)
	timer_status = context_dict["timer_status"]
	if timer_status==EAS.TIMER_ENDED:
		return base_response(request, exam_ended_str)
	elif timer_status!=EAS.TIMER_IN_PROGRESS:
		return base_response(request, exam_not_started_str)
	fill_dict_with_sas_values(context_dict,sas)
	fill_dict_with_answer_values(context_dict,answer)
	if not context_dict["is_attable"]:
		return base_response(request, "You don't have any more attempts left for this question.")
	unlocked = context_dict["unlocked"]
	if not unlocked:
		return base_response(request, "This section is locked")
	if not context_dict["is_attable2"]:
		return base_response(request, "You cannot answer more questions from this section")

	# save response to database
	qtype = context_dict["qtype"]
	special_answer = context_dict["special_answer"]
	if qtype=="text":
		if "response" not in request.POST:
			raise InvalidFormData()
		response = request.POST["response"]
		special_answer.response = response
		if response:
			answer.attempts+=1
	elif qtype=="mcq":
		special_answer.chosen_options.clear()
		chosen_option_ids = request.POST.getlist("response")
		for option_id in chosen_option_ids:
			link = McqAnswerToMcqOption(mcq_answer=special_answer,mcq_option_id=option_id)
			link.save()
		if chosen_option_ids:
			answer.attempts+=1
	else:
		raise QuestionTypeNotImplemented(qtype)
	answer.save()
	special_answer.save()

	# redirect
	if "submit" in request.POST:
		nextaid = aid
	elif "submit_and_next" in request.POST:
		nextaid = context_dict["nextaid"]
	else:
		raise InvalidFormData()
	if not nextaid:
		nextsid = context_dict["nextsid"]
		if not nextsid:
			nextaid = aid
		else:
			return HttpResponseRedirect(reverse("main:sas_cover",args=(nextsid,)))
	return HttpResponseRedirect(reverse("main:answer",args=(nextaid,)))

@login_required
def submit_eas(request,eid):
	if request.method!="POST":
		raise Http404("This page is only accessible via POST")
	eas = get_object_or_404(ExamAnswerSheet,id=eid)
	if eas.user!=request.user:
		raise Http404(InvalidUser.exp_str)
	timer_status = eas.get_timer_status()
	if timer_status == EAS.TIMER_IN_PROGRESS:
		eas.end_time = timezone.now()
		eas.save()
	elif timer_status == EAS.TIMER_NOT_STARTED:
		eas.end_time = eas.start_time
		eas.save()
	return HttpResponseRedirect(reverse("main:eas_cover",args=(eas.id,)))

"""
This module adds an ExamAnswerSheet and its subordinate elements to the database for any given Exam and User object.
It can add SectionAnswerSheet and Answer objects in a different order to simulate shuffling sections and questions.
Currently shuffling options is not supported.
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
if BASE_DIR not in sys.path:
	sys.path.append(BASE_DIR)

import random
import custom_exceptions

def add_answer(question,sas,shuffle_options=None):
	"""
	Adds an Answer object to database which is bound to the section and eas.
	shuffle_options is defined like in add_eas
	"""
	answer = Answer(section_answer_sheet=sas)
	answer.save()
	# create special answer which is bound to question's specialization
	special_question = question.get_special_question()
	qtype = special_question.get_qtype()
	if qtype=="text":
		special_answer = TextAnswer(special_question=special_question, answer=answer)
	elif qtype=="mcq":
		special_answer = McqAnswer(special_question=special_question, answer=answer)
	else:
		raise custom_exceptions.QuestionTypeNotImplemented
	special_answer.save()
	return answer

def add_sas(section,eas,shuffle_questions=None,shuffle_options=None):
	"""
	Adds a SectionAnswerSheet object to database which is bound to the section and eas.
	shuffle_questions and shuffle_options are defined like in add_eas
	"""
	sas = SectionAnswerSheet(section=section, exam_answer_sheet=eas)
	sas.save()
	# add answers
	if shuffle_questions!=True and shuffle_questions!=False:
		shuffle_questions = section.shuffle_questions
	if shuffle_questions:
		questions = list(section.question_set.all())
		random.shuffle(questions)
	else:
		questions = list(section.question_set.order_by('id'))
	for ques in questions:
		add_answer(ques,sas,shuffle_options)
	return sas

def add_eas(exam,user,shuffle_sections=None,shuffle_questions=None,shuffle_options=None):
	"""
	Adds an ExamAnswerSheet object to database which is bound to exam and user.
	If shuffle_sections is True, randomly shuffles sections.
	If shuffle_sections is False, does not shuffle sections.
	If shuffle_sections is something else, decides shuffling using exam.shuffle_sections.
	shuffle_questions and shuffle_options are similarly defined
	"""
	eas = ExamAnswerSheet(exam=exam,user=user)
	eas.save()
	# add SectionAnswerSheets
	if shuffle_sections!=True and shuffle_sections!=False:
		shuffle_sections = exam.shuffle_sections
	if shuffle_sections:
		sections = list(exam.section_set.all())
		random.shuffle(sections)
	else:
		sections = list(exam.section_set.order_by('id'))
	for section in sections:
		add_sas(section,eas,shuffle_questions,shuffle_options)
	return eas

if __name__=="__main__":
	os.environ.setdefault('DJANGO_SETTINGS_MODULE','project_conf.settings')
	print("Setting up Django ...")
	import django
	django.setup()

from main.models import Exam, ExamAnswerSheet, SectionAnswerSheet, Answer, TextAnswer, McqAnswer
from django.contrib.auth.models import User
import sys

def main(exam_name,username):
	exam = Exam.objects.get(name=exam_name)
	user = User.objects.get(username=username)
	add_eas(exam,user)

if __name__=="__main__":
	if len(sys.argv)<=1:
		exam_name = input("Enter exam name: ")
	else:
		exam_name = sys.argv[1]
	if len(sys.argv)<=2:
		username = input("Enter username: ")
	else:
		username = sys.argv[2]
	print("Adding ExamAnswerSheet ...")
	main(exam_name,username)

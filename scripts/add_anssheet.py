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
from main.models import ExamAnswerSheet, SectionAnswerSheet, Answer, TextAnswer, McqAnswer
import custom_exceptions

def add_answer(question,sas,shuffle_options=None):
	"""
	Adds an Answer object to database which is bound to the section and eas.
	shuffle_options is defined like in add_eas
	"""
	answer = Answer(section_answer_sheet=sas)
	answer.save()
	# create child answer which is bound to question's child
	child_question = question.get_child_question()
	qtype = child_question.get_qtype()
	if qtype=="text":
		child_answer = TextAnswer(text_question=child_question, answer=answer)
	elif qtype=="mcq":
		child_answer = McqAnswer(mcq_question=child_question, answer=answer)
	else:
		raise custom_exceptions.QuestionTypeNotImplemented
	child_answer.save()

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

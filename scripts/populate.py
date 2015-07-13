"""
This module loads an exam, section or question from a dict and adds it to the database.
Note that it does not validate the dict. You have to do that yourself. If you want to load the dict from a JSON file, you can use the validation module.
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
if BASE_DIR not in sys.path:
	sys.path.append(BASE_DIR)

import json
from scripts import validation

class QuestionTypeNotImplementedError(NotImplementedError):
	qtype = "Unspecified"
	def __init__(self,qtype):
		self.qtype=qtype
	def __str__(self):
		return "Questions of type "+qtype+" are not yet supported"

def add_options(mcq_question_in_db,options_list,correct_status):
	"""
	Adds all options in options_list to mcq_question_in_db
	Note that elements of options_list are not instances of models.McqOption,
	they are objects which match the mcq_option JSON schema.
	This function makes a models.McqOption instance for each option and saves that to database.
	The mcq_question ForeignKey of those instances will point to mcq_question_in_db.
	If correct_status is True, all options are added with is_correct BooleanField set to True.
	If correct_status is False, all options are added with is_correct BooleanField set to False.
	Otherwise, is_correct BooleanField of options is derived from the "is_correct" key of each object, if it is a dict;
	if it is not a dict or the "is_correct" key is absent, the default value of the is_correct BooleanField will be used
	"""
	boolean_correct_status= (correct_status==True or correct_status==False)
	for option in options_list:
		mcq_option = McqOption(mcq_question=mcq_question_in_db)
		if boolean_correct_status:
			mcq_option.is_correct = correct_status
		if type(option)==str:
			mcq_option.text=option
		else:
			if "title" in option:
				mcq_option.title=option["title"]
			mcq_option.text=option["text"]
			if not boolean_correct_status and "is_correct" in option:
				mcq_option.is_correct = option["is_correct"]
		mcq_option.save()

def add_question(section_in_db,question_dict):
	# add generic stuff
	question = Question()
	valid_properties = validation.schema["question"]["properties"]
	special_properties = ["metadata","tags"]
	for key in question_dict:
		if key in valid_properties and key not in special_properties and hasattr(question,key):
			setattr(question,key,question_dict[key])
		# It was planned at the beginning of the project that useless keys 
		# will be added as JSON to the metadata field of models.Question
		# but implementing that seems to be difficult so I'm leaving it out for now
	question.section = section_in_db
	question.save()

	# add type-specific stuff
	qtype = question_dict["type"]

	if qtype=="text" or qtype=="regex":
		text_question = TextQuestion(question=question)
		text_question.correct_answer = question_dict["answer"]
		if "ignore_case" in question_dict:
			text_question.ignore_case = question_dict["ignore_case"]
		if "use_regex" in question_dict:
			text_question.use_regex = question_dict["use_regex"]
		elif qtype=="regex":
			text_question.use_regex = True
		text_question.save()

	elif qtype=="mcq" or qtype=="mmcq":
		mcq_question = McqQuestion(question=question)
		if "multicorrect" in question_dict:
			mcq_question.multicorrect = question_dict["multicorrect"]
		elif qtype=="mmcq":
			mcq_question.multicorrect = True
		mcq_question.save()
		if "options" in question_dict:
			add_options(mcq_question,question_dict["options"],None)
		if "correct_options" in question_dict:
			add_options(mcq_question,question_dict["correct_options"],True)
		if "wrong_options" in question_dict:
			add_options(mcq_question,question_dict["wrong_options"],False)
		mcq_question.verify_correct_options()

	else:
		raise QuestionTypeNotImplementedError(qtype)

def add_section(exam_in_db,section_dict):
	# add simple properties
	properties_to_add=["name","info","comment"]
	section = Section()
	for key in properties_to_add:
		if key in section_dict and hasattr(section,key):
			setattr(section,key,section_dict[key])
	section.exam = exam_in_db
	section.save()

	# add questions
	for question_dict in section_dict["questions"]:
		add_question(section,question_dict)

def add_exam(exam_dict,print_messages=False):
	# add simple properties
	valid_properties = validation.schema["exam"]["properties"]
	special_properties = ["tags","time_limit"]
	exam = Exam()
	for key in exam_dict:
		if key in valid_properties and key not in special_properties and hasattr(exam,key):
			setattr(exam,key,exam_dict[key])
	exam.save()

	# add sections
	for section_dict in exam_dict["sections"]:
		if print_messages:
			print("Adding section:",section_dict["name"],"...")
		add_section(exam,section_dict)

def main(*args):
#	print("args:",args)
	for rel_path in args:
		exam_path = os.path.abspath(rel_path)
		print("Reading and validating exam file:",rel_path,"...")
		exam_dict = validation.validate_and_get_exam(exam_path)
		print("Adding exam:",exam_dict["name"],"...")
		add_exam(exam_dict,True)

if __name__=="__main__":
	os.environ.setdefault('DJANGO_SETTINGS_MODULE','owliver.settings')
	print("Setting up Django ...")
	import django
	django.setup()

from main.models import Exam, Section, Question, TextQuestion, McqQuestion, McqOption
if __name__=="__main__":
	main(*(sys.argv[1:]))

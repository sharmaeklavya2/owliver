# This script clears the database of all exams, tags and/or queries

import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
	sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE','owliver.settings')
print("Setting up Django ...")
import django
django.setup()

from main.models import Exam, Tag, ExamAnswerSheet
from django.contrib.auth.models import User

for arg in sys.argv[1:]:
	arg=arg.lower()
	if arg=="exam" or arg=="exams":
		print("Clearing all exams ...")
		Exam.objects.all().delete()
	elif arg=="eas" or arg=="examanswersheet":
		print("Clearing all exam_answer_sheets ...")
		ExamAnswerSheet.objects.all().delete()
	elif arg=="tag" or arg=="tags":
		print("Clearing all tags ...")
		Tag.objects.all().delete()
	elif arg=="user" or arg=="users":
		print("Clearing all users ...")
		User.objects.all().delete()


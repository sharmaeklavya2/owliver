# This scripts clears the database of all exams

import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
	sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE','owliver.settings')
print("Setting up Django ...")
import django
django.setup()

from main.models import Exam
print("Clearing all exams ...")
Exam.objects.all().delete()

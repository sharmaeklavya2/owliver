from django.shortcuts import get_object_or_404
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


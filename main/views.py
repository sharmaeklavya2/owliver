from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

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

from django.shortcuts import render
from django.http import HttpResponse
from django import get_version

import sys

def get_python_version():
	return ".".join([str(sys.version_info.major),str(sys.version_info.minor)])
def get_django_version():
	return get_version()[:4]

def about(request):
	context_dict = {}
	context_dict["python_version"] = get_python_version()
	context_dict["django_version"] = get_django_version()
	context_dict["contributors"] = ["Eklavya Sharma"]
	return render(request,"about.html",context_dict)

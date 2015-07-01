from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def about(request):
	return HttpResponse("Owliver is a site to make and take tests.\nCreated by Eklavya Sharma using Python 3.4 and Django 1.8")

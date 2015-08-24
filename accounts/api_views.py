from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_safe, require_POST

from collections import OrderedDict
import json

@require_safe
def account_info(request):
	user = request.user
	if user.is_authenticated():
		fields = ["username", "first_name", "last_name", "email", "is_staff", "is_superuser"]
		fields2 = ["last_login", "date_joined"]
		response_dict = OrderedDict()
		for field in fields:
			response_dict[field] = getattr(user,field)
		for field in fields2:
			response_dict[field] = str(getattr(user,field))
		response_dict["groups"] = list(user.groups.order_by("name"))
	else:
		response_dict = {"error":"not_logged_in"}
	return HttpResponse(json.dumps(response_dict,indent=2), content_type="application/json")

@require_POST
def login_view(request):
	response_dict = {}
	if "username" in request.POST and "password" in request.POST and request.POST["username"] and request.POST["password"]:
		username = request.POST["username"]
		password = request.POST["password"]
		user = authenticate(username=username,password=password)
		if not user:
			response_dict["error"] = "wrong_login"
		elif not user.is_active:
			context_dict["error"] = "inactive_account"
		else:
			login(request,user)
	else:
		response_dict["error"] = "invalid_request"
	return JsonResponse(response_dict)

@require_POST
def logout_view(request):
	logout(request)
	return HttpResponse("", content_type="application/json")


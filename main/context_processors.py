from django.conf import settings

def settings_processor(request):
	return {
		"settings": settings,
		"PROJECT_NAME": settings.PROJECT_NAME,
	}

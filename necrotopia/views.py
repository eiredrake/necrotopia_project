from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from Config import Config
from necrotopia_project.settings import GLOBAL_SITE_NAME, STATICFILES_DIR


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> HttpResponse:
    file = (STATICFILES_DIR / "images" / "project_icon.png").open("rb")
    return FileResponse(file)


# Create your views here.
def home(request):
    template = 'necrotopia/home.html'
    if not Config.LIVE_SITE_OPEN:
        template = 'necrotopia/coming_soon.html'

    context = {
        "title": GLOBAL_SITE_NAME,
    }

    return render(request, template, context=context)


def register(request):
    template = 'registration/signup.html'

    return render(request, template)


def login(request):
    template = 'registration/login.html'

    return render(request, template)

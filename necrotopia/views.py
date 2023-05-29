import re

from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import render
from django.template import RequestContext
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.contrib.auth import login as auth_login
from Config import Config
from necrotopia.forms import LoginForm, CustomUserCreationForm
from necrotopia_project import settings
from necrotopia_project.settings import GLOBAL_SITE_NAME, STATICFILES_DIR
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth import login, authenticate


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


def register(request, redirect_to=settings.LOGIN_REDIRECT_URL, template_name='registration/signup.html', creation_form=CustomUserCreationForm):
    if request.method == "POST":
        form = creation_form(data=request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()

            username = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')

            user = authenticate(username=user.email, password=raw_password)
            login(request, user)

            messages.success(request, message="Your account has been created")

            return HttpResponseRedirect(redirect_to)
        else:
            print(form.errors)
    else:
        form = creation_form(request)

    new_context = {
        'title': GLOBAL_SITE_NAME,
        'form': form,
    }

    return render(request=request, template_name=template_name, context=new_context)


def log_me_out(request):
    logout(request)
    redirect_to = settings.LOGIN_REDIRECT_URL

    messages.success(request, message="You have been logged out")

    return HttpResponseRedirect(redirect_to)


def authenticate_user(request, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME, authentication_form=LoginForm):
    redirect_to = settings.LOGIN_REDIRECT_URL

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            if not redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            elif '//' in redirect_to and re.match(r'[$\?]*//', redirect_to):
                redirect_to = settings.LOGIN_REDIRECT_URL

            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)

            user = form.get_user()
            auth_login(request, user)

            messages.success(request, message="You have been logged in as {user}".format(user=user.email))

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    new_context = {
        'title': GLOBAL_SITE_NAME,
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name
    }
    context = RequestContext(request)
    context.update(new_context)

    return render(request=request, template_name=template_name, context=new_context)

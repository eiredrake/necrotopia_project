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
from necrotopia.forms import LoginForm
from necrotopia_project import settings
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


def login(request, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME, authentication_form=LoginForm):
    redirect_to = settings.LOGIN_REDIRECT_URL

    # redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            if not redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            elif '//' in redirect_to and re.match(r'[$\?]*//', redirect_to):
                redirect_to = settings.LOGIN_REDIRECT_URL

            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)

            auth_login(request, form.get_user())

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



# def login(request):
#     context = {
#         "title": GLOBAL_SITE_NAME,
#     }
#
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#         else:
#             form = LoginForm()
#
#         context['form'] = form
#
#         render(request, 'registration/login.html', context=context)


    #     # Process the request if posted data are available
    #     username = request.POST['username']
    #     password = request.POST['password']
    #     remember_me = request
    #     # Check username and password combination if correct
    #     user = authenticate(username=username, password=password)
    #     if user is not None:
    #         # Save session as cookie to login the user
    #         login(request, user)
    #         # Success, now let's login the user.
    #         return render(request, 'necrotopia/home.html', context=context)
    #     else:
    #         # Incorrect credentials, let's throw an error to the screen.
    #         context["error_message"] = 'Incorrect username and / or password.'
    #
    #         return render(request, 'registration/login.html', context=context)
    # else:
    #     # No post data available, let's just show the page to the user.
    #     return render(request, 'registration/login.html', context=context)

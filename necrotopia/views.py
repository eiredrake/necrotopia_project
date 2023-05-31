import re

from django.contrib.auth import authenticate, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.contrib.auth import login as auth_login
from Config import Config
from necrotopia.forms import AuthenticateUserForm, RegisterUserForm
from necrotopia.models import UserProfile
from necrotopia.token import account_activation_token
from necrotopia_project import settings
from necrotopia_project.settings import GLOBAL_SITE_NAME, STATICFILES_DIR
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.utils.translation import gettext_lazy as _translate
from django.utils.encoding import force_str

@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> FileResponse:
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


def log_me_out(request):
    logout(request)
    redirect_to = settings.LOGIN_REDIRECT_URL

    messages.success(request, message=_translate("You have been logged out"))

    return HttpResponseRedirect(redirect_to)


def authenticate_user(request, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME,
                      authentication_form=AuthenticateUserForm):
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

            messages.success(request, message=_translate("You have been logged in as {user}").format(user=user.email))

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
        else:
            new_context = {'form': form, 'title': GLOBAL_SITE_NAME}

            return render(request, template_name, new_context)
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


def send_registration_email(request, user):
    current_site = get_current_site(request)
    mail_subject = 'Activation link has been sent to your specified email'
    message = render_to_string('registration/activation_email.html',
                               {
                                   'user': user,
                                   'domain': current_site.domain,
                                   'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                   'token': account_activation_token.make_token(user),
                               })

    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = 'html'
    email.send()


def register_user(request):
    redirect_to = settings.LOGIN_REDIRECT_URL

    context = {}
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False  # deactivate until account is confirmed
            user.save()

            send_registration_email(request, user)

            messages.success(request, message=_translate("Your user has been created!"))

            return HttpResponseRedirect(redirect_to)
        else:
            messages.error(request, message=_translate("User account not created"))
    else:
        form = RegisterUserForm

    context['form'] = form

    return render(request, 'registration/user_registration.html', context=context)


class ActivateAccount(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserProfile.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.email_confirmed = True
            user.save()
            login(request, user)
            messages.success(request, _translate('Your account has been confirmed.'))
            return redirect('home')
        else:
            messages.warning(request, _translate('The confirmation link was invalid, possibly because it has already been used.'))
            return redirect('home')


def user_profile_change(request):
    return None
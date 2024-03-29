import re

import tagging
from django.contrib.auth import authenticate, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import QuerySet
from django.http import FileResponse, HttpRequest, HttpResponse, HttpResponseRedirect, Http404
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
from tagging.models import TaggedItem

from Config import Config
from necrotopia.forms import AuthenticateUserForm, RegisterUserForm, UserProfileForm
from necrotopia.models import UserProfile, Rule, RulePicture, ModuleAssembly, Advertisement, ItemPicture, ModuleGrade, \
    SkillItem, SkillRatings, ResourceItem
from necrotopia.token import account_activation_token
from necrotopia_project import settings
from necrotopia_project.settings import GLOBAL_SITE_NAME, STATICFILES_DIRS
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.utils.translation import gettext_lazy as _translate
from django.utils.encoding import force_str
from django.utils import timezone


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> FileResponse:
    file = (STATICFILES_DIRS / "images" / "project_icon.png").open("rb")
    return FileResponse(file)


def get_active_advertisements_for_user(user: UserProfile):
    now = timezone.now()

    if user.is_anonymous or user.display_game_advertisements:
        return Advertisement.objects.filter(published=True, start_date__lte=now, end_date__gte=now)
    else:
        return None


# Create your views here.
def home(request):
    template = 'necrotopia/home.html'

    advertisements = get_active_advertisements_for_user(request.user)

    context = {
        "title": GLOBAL_SITE_NAME,
        'advertisements': advertisements
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
            messages.warning(request, _translate(
                'The confirmation link was invalid, possibly because it has already been used.'))
            return redirect('home')


def user_profile_change(request, template='necrotopia/user_profile_change.html'):
    context = {'user': request.user, 'title': GLOBAL_SITE_NAME}
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user.display_name = form.cleaned_data['display_name']
            user.full_name = form.cleaned_data['full_name']
            user.title = form.cleaned_data['title']
            user.gender = form.cleaned_data['gender']
            user.display_game_advertisements = form.cleaned_data['display_game_advertisements']
            user.pronouns = form.cleaned_data['pronouns']

            user.save()
        else:
            pass
    else:
        form = UserProfileForm(instance=user)

    context['form'] = form

    return render(request, template, context=context)


def tag_OR_query(model, tags):
    result = TaggedItem.objects.none()
    for tag in tags:
        result = result.union(TaggedItem.objects.get_by_model(model, tag))

    return result


def search_results(request):
    search_terms = []
    all_rules_found = []
    context = {'title': GLOBAL_SITE_NAME, 'search_terms': search_terms}

    if request.method == 'POST':
        search_terms = request.POST['search_terms']
        search_terms_list = list(search_terms.lower().split(','))

        tags = tagging.models.get_tag_list(search_terms)

        blueprints_by_name = ModuleAssembly.objects.filter(name__icontains=search_terms)
        blueprints_by_tag = tag_OR_query(model=ModuleAssembly, tags=tags)
        all_blueprints_found = blueprints_by_name.union(blueprints_by_tag).order_by('name')

        rules_by_name = Rule.objects.filter(name__icontains=search_terms)
        rules_by_tag = tag_OR_query(model=Rule, tags=tags)
        all_rules_found = rules_by_name.union(rules_by_tag).order_by('name')

        skills_by_name = SkillItem.objects.filter(name__icontains=search_terms)
        skills_by_tag = tag_OR_query(model=SkillItem, tags=tags)
        all_skills_found = skills_by_name.union(skills_by_tag).order_by('name')

        resource_by_name = ResourceItem.objects.filter(name__icontains=search_terms)
        resource_by_tag = tag_OR_query(model=ResourceItem, tags=tags)
        all_resources_found = resource_by_name.union(resource_by_tag).order_by('name')

        context['all_blueprints_found'] = all_blueprints_found
        context['all_skills_found'] = all_skills_found
        context['all_rules_found'] = all_rules_found
        context['all_resources_found'] = all_resources_found
        # context['all_chapters_found'] = all_chapters_found
        context['search_terms'] = search_terms_list
        context['title'] = GLOBAL_SITE_NAME

    return render(request, 'necrotopia/search_results.html', context)


def rules_list(request):
    return render(request, 'necrotopia/rules_list.html', context={"rules_found": Rule.objects.all()})


def rule_view(request, rule_id):
    try:
        rule = Rule.objects.get(pk=rule_id)
        pictures = RulePicture.objects.filter(rule_item_id=rule_id)
    except Rule.DoesNotExist:
        raise Http404("That rule does not exist")
    context = {
        'rule': rule,
        'pictures': pictures,
        'title': GLOBAL_SITE_NAME,
    }
    return render(request, 'necrotopia/rule_view.html', context=context)


def blueprint_view(request, blueprint_id):
    try:
        blueprint = ModuleAssembly.objects.get(pk=blueprint_id)
        # pictures = ItemPicture.objects.filter(assembly_item_id=blueprint_id)
        module_grades = ModuleGrade.objects.filter(module_assembly=blueprint)
        parts_list = blueprint.flatten()

        tags = blueprint.get_tags_string()
    except ModuleAssembly.DoesNotExist:
        raise Http404("That blueprint does not exist")

    return render(request, 'necrotopia/blueprint_view.html',
                  context={
                      'blueprint': blueprint,
                      'item_type': blueprint.get_item_type_display,
                      'expiration': blueprint.get_expiration(),
                      # 'pictures': pictures,
                      'module_grades': module_grades,
                      'tags': tags,
                      'parts_list': parts_list,
                      'title': GLOBAL_SITE_NAME,
                  })


def skill_list(request):
    return render(request, 'necrotopia/skill_list.html', context={'skills_found': SkillItem.objects.all()})


def skill_view(request, skill_id):
    try:
        skill = SkillItem.objects.get(pk=skill_id)
        skill_ratings = SkillRatings.objects.filter(skill_id=skill.id)
    except SkillItem.DoesNotExist:
        raise Http404("That skill does not exist")
    context = {
        'skill': skill,
        'skill_ratings': skill_ratings,
        'title': GLOBAL_SITE_NAME
    }

    return render(request, 'necrotopia/skill_view.html', context=context)


def resources_list(request, resources):
    return render(request, 'necrotopia/resource_list.html', context=resources)


def resource_view(request, resource_id):
    try:
        resource = ResourceItem.objects.get(pk=resource_id)
    except Rule.DoesNotExist:
        raise Http404("That resource does not exist")
    context = {
        'resource': resource,
    }
    return render(request, 'necrotopia/resource_view.html', context=context)



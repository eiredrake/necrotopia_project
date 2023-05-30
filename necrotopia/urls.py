from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path, reverse_lazy, re_path, include
from django.contrib import admin
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('authenticate_user', views.authenticate_user, name='authenticate_user')
] + staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

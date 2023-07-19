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
    path('search_results/', views.search_results, name='search_results'),
    path('rule_view/<int:rule_id>', views.rule_view, name='rule_view'),
    path('rules_list/', views.rules_list, name='rules_list'),
    path('blueprint_view/<int:blueprint_id>', views.blueprint_view, name='blueprint_view'),
] + staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


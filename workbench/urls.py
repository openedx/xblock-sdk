"""Provide XBlock urls"""


from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.urls import re_path

from workbench import views

admin.autodiscover()

urlpatterns = [
    path('', views.index, name='workbench_index'),
    path(
        'scenario/<str:scenario_id>/<str:view_name>/',
        views.show_scenario,
        name='scenario'
    ),
    path('userlist/',
        views.user_list,
        name='userlist'),
    path(
        'scenario/<str:scenario_id>/',
        views.show_scenario,
        name='workbench_show_scenario'
    ),
    path(
        'view/<str:scenario_id>/<str:view_name>/',
        views.show_scenario,
        {'template': 'workbench/blockview.html'}
    ),
    path(
        'view/<str:scenario_id>/',
        views.show_scenario,
        {'template': 'workbench/blockview.html'}
    ),
    re_path(
        r'^handler/(?P<usage_id>[^/]+)/(?P<handler_slug>[^/]*)(?:/(?P<suffix>.*))?$',
        views.handler, {'authenticated': True},
        name='handler'
    ),
    re_path(
        r'^aside_handler/(?P<aside_id>[^/]+)/(?P<handler_slug>[^/]*)(?:/(?P<suffix>.*))?$',
        views.aside_handler, {'authenticated': True},
        name='aside_handler'
    ),
    re_path(
        r'^unauth_handler/(?P<usage_id>[^/]+)/(?P<handler_slug>[^/]*)(?:/(?P<suffix>.*))?$',
        views.handler, {'authenticated': False},
        name='unauth_handler'
    ),
    re_path(
        r'^resource/(?P<block_type>[^/]+)/(?P<resource>.*)$',
        views.package_resource,
        name='package_resource'
    ),
    path(
        'reset_state',
        views.reset_state,
        name='reset_state'
    ),

    re_path(r'^admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""Provide XBlock urls"""



from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from workbench import views

admin.autodiscover()

urlpatterns = [
    url(r'^$', views.index, name='workbench_index'),
    url(
        r'^scenario/(?P<scenario_id>[^/]+)/(?P<view_name>[^/]+)/$',
        views.show_scenario,
        name='scenario'
    ),
    url(r'^userlist/$',
        views.user_list,
        name='userlist'),
    url(
        r'^scenario/(?P<scenario_id>[^/]+)/$',
        views.show_scenario,
        name='workbench_show_scenario'
    ),
    url(
        r'^view/(?P<scenario_id>[^/]+)/(?P<view_name>[^/]+)/$',
        views.show_scenario,
        {'template': 'workbench/blockview.html'}
    ),
    url(
        r'^view/(?P<scenario_id>[^/]+)/$',
        views.show_scenario,
        {'template': 'workbench/blockview.html'}
    ),
    url(
        r'^handler/(?P<usage_id>[^/]+)/(?P<handler_slug>[^/]*)(?:/(?P<suffix>.*))?$',
        views.handler, {'authenticated': True},
        name='handler'
    ),
    url(
        r'^aside_handler/(?P<aside_id>[^/]+)/(?P<handler_slug>[^/]*)(?:/(?P<suffix>.*))?$',
        views.aside_handler, {'authenticated': True},
        name='aside_handler'
    ),
    url(
        r'^unauth_handler/(?P<usage_id>[^/]+)/(?P<handler_slug>[^/]*)(?:/(?P<suffix>.*))?$',
        views.handler, {'authenticated': False},
        name='unauth_handler'
    ),
    url(
        r'^resource/(?P<block_type>[^/]+)/(?P<resource>.*)$',
        views.package_resource,
        name='package_resource'
    ),
    url(
        r'^reset_state$',
        views.reset_state,
        name='reset_state'
    ),

    url(r'^admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()

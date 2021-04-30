"""Django views implementing the XBlock workbench.

This code is in the Workbench layer.

"""



import logging
import mimetypes

from xblock.core import XBlock, XBlockAside
from xblock.django.request import django_to_webob_request, webob_to_django_response
from xblock.exceptions import NoSuchUsage
from xblock.plugin import PluginMissingError

from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from .models import XBlockState
from .runtime import WorkbenchRuntime
from .runtime_util import reset_global_state
from .scenarios import get_scenarios

log = logging.getLogger(__name__)


# We don't really have authentication and multiple students, just accept their
# id on the URL.
def get_student_id(request):
    """Get the student_id from the given request."""
    student_id = request.GET.get('student', 'student_1')
    return student_id


# ---- Views -----

def index(_request):
    """Render `index.html`"""
    the_scenarios = sorted(get_scenarios().items())
    the_scenarios = [
        (class_name, scenario)
        for class_name, scenario in the_scenarios
        if class_name.split('.')[0] not in settings.EXCLUDED_XBLOCKS
    ]
    return render(_request, 'workbench/index.html', {
        'scenarios': [(desc, scenario.description) for desc, scenario in the_scenarios]
    })


@ensure_csrf_cookie
def show_scenario(request, scenario_id, view_name='student_view', template='workbench/block.html'):
    """
    Render the given `scenario_id` for the given `view_name`, on the provided `template`.

    `view_name` defaults to 'student_view'.
    `template` defaults to 'block.html'.

    """
    student_id = get_student_id(request)
    log.info("Start show_scenario %r for student %s", scenario_id, student_id)

    try:
        scenario = get_scenarios()[scenario_id]
    except KeyError as ex:
        raise Http404 from ex

    usage_id = scenario.usage_id
    runtime = WorkbenchRuntime(student_id)
    block = runtime.get_block(usage_id)
    render_context = {
        'activate_block_id': request.GET.get('activate_block_id', None)
    }

    frag = block.render(view_name, render_context)
    log.info("End show_scenario %s", scenario_id)
    return render(request, template, {
        'scenario': scenario,
        'block': block,
        'body': frag.body_html(),
        'head_html': frag.head_html(),
        'foot_html': frag.foot_html(),
        'student_id': student_id,
    })


def user_list(_request):
    """
    This will return a list of all users in the database
    """
    # We'd really like to do .distinct, but sqlite+django does not support this;
    # hence the hack with sorted(set(...))
    users = sorted(
        user_id[0]
        for user_id in set(XBlockState.objects.values_list('user_id'))
    )
    return JsonResponse(users, safe=False)


def handler(request, usage_id, handler_slug, suffix='', authenticated=True):
    """The view function for authenticated handler requests."""
    if authenticated:
        student_id = get_student_id(request)
        log.info("Start handler %s/%s for student %s", usage_id, handler_slug, student_id)
    else:
        student_id = "none"
        log.info("Start handler %s/%s", usage_id, handler_slug)

    runtime = WorkbenchRuntime(student_id)

    try:
        block = runtime.get_block(usage_id)
    except NoSuchUsage as ex:
        raise Http404 from ex

    request = django_to_webob_request(request)
    request.path_info_pop()
    request.path_info_pop()
    result = block.runtime.handle(block, handler_slug, request, suffix)
    log.info("End handler %s/%s", usage_id, handler_slug)
    return webob_to_django_response(result)


def aside_handler(request, aside_id, handler_slug, suffix='', authenticated=True):
    """The view function for authenticated handler requests."""
    if authenticated:
        student_id = get_student_id(request)
        log.info("Start handler %s/%s for student %s", aside_id, handler_slug, student_id)
    else:
        student_id = "none"
        log.info("Start handler %s/%s", aside_id, handler_slug)

    runtime = WorkbenchRuntime(student_id)

    try:
        block = runtime.get_aside(aside_id)
    except NoSuchUsage as ex:
        raise Http404 from ex

    request = django_to_webob_request(request)
    request.path_info_pop()
    request.path_info_pop()
    result = block.runtime.handle(block, handler_slug, request, suffix)
    log.info("End handler %s/%s", aside_id, handler_slug)
    return webob_to_django_response(result)


def package_resource(_request, block_type, resource):
    """
    Wrapper for `pkg_resources` that tries to access a resource and, if it
    is not found, raises an Http404 error.
    """
    try:
        xblock_class = XBlock.load_class(block_type)
    except PluginMissingError:
        try:
            xblock_class = XBlockAside.load_class(block_type)
        except PluginMissingError as ex:
            raise Http404 from ex
    try:
        content = xblock_class.open_local_resource(resource)
    except Exception as ex:
        raise Http404 from ex
    mimetype, _ = mimetypes.guess_type(resource)
    return HttpResponse(content, content_type=mimetype)


@csrf_exempt
def reset_state(request):
    """Delete all state and reload the scenarios."""
    log.info("RESETTING ALL STATE")
    reset_global_state()
    referrer_url = request.META['HTTP_REFERER']

    return redirect(referrer_url)

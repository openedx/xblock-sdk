"""Django views implementing the XBlock workbench.

This code is in the Workbench layer.

"""

import json
import logging
import mimetypes
from StringIO import StringIO

from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render_to_response
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from xblock.core import XBlock
from xblock.django.request import webob_to_django_response, django_to_webob_request
from xblock.exceptions import NoSuchUsage

from .models import XBlockState
from .runtime import WorkbenchRuntime, reset_global_state
from .scenarios import SCENARIOS, FAILURES


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
    the_scenarios = sorted(SCENARIOS.items())
    failures = []
    for failure in FAILURES:
        failures.append([
            failure["name"],
            type(failure["exception"]).__name__,
        ])
        try:
            failures[-1].extend([failure["exception"].args[0]])
        except:
            failures[-1].extend([None])
        try:
            failures[-1].extend([
                True,
                failure["exception"].args[1][0],
                failure["exception"].args[1][1],
                failure["exception"].args[1][2],
                failure["exception"].args[1][3]
            ])
        except:
            failures[-1].extend([False, None, None, None, None])
    return render_to_response('workbench/index.html', {
        'scenarios': [(desc, scenario.description) for desc, scenario in the_scenarios],
        'failures': failures
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
        scenario = SCENARIOS[scenario_id]
    except KeyError:
        raise Http404

    usage_id = scenario.usage_id
    runtime = WorkbenchRuntime(student_id)
    block = runtime.get_block(usage_id)
    frag = block.render(view_name)
    log.info("End show_scenario %s", scenario_id)
    return render_to_response(template, {
        'scenario': scenario,
        'block': block,
        'body': frag.body_html(),
        'head_html': frag.head_html(),
        'foot_html': frag.foot_html(),
        'student_id': student_id,
    })


def user_list(request):
    """
    This will return a list of all users in the database
    """
    # We'd really like to do .distinct, but sqlite+django does not support this;
    # hence the hack with sorted(set(...))
    user_list = sorted(x[0] for x in set(XBlockState.objects.values_list('user_id')))
    return HttpResponse(json.dumps(user_list, indent=2), content_type="application/json")


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
    except NoSuchUsage:
        raise Http404

    request = django_to_webob_request(request)
    request.path_info_pop()
    request.path_info_pop()
    result = block.runtime.handle(block, handler_slug, request, suffix)
    log.info("End handler %s/%s", usage_id, handler_slug)
    return webob_to_django_response(result)


def package_resource(_request, block_type, resource):
    """
    Wrapper for `pkg_resources` that tries to access a resource and, if it
    is not found, raises an Http404 error.
    """
    try:
        xblock_class = XBlock.load_class(block_type)
        content = xblock_class.open_local_resource(resource)
    except Exception:  # pylint: disable-msg=broad-except
        raise Http404
    mimetype, _ = mimetypes.guess_type(resource)
    return HttpResponse(content, mimetype=mimetype)


@csrf_exempt
def reset_state(request):
    """Delete all state and reload the scenarios."""
    log.info("RESETTING ALL STATE")
    reset_global_state()
    referrer_url = request.META['HTTP_REFERER']

    return redirect(referrer_url)

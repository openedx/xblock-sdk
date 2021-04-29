"""Test the workbench views."""


import functools
import json

import pytest
from web_fragments.fragment import Fragment
from webob import Response
from xblock.core import Scope, String, XBlock
from xblock.exceptions import DisallowedFileError
from xblock.runtime import NoSuchHandlerError

from django.test.client import Client
from django.urls import reverse

from workbench import scenarios
from workbench.runtime import ID_MANAGER

pytestmark = pytest.mark.django_db


def temp_scenario(temp_class, scenario_name='test_scenario'):
    """Create a temporary scenario that uses `temp_class`."""
    def _decorator(func):
        @functools.wraps(func)
        @XBlock.register_temp_plugin(temp_class)
        def _inner(*args, **kwargs):
            # Create a scenario, just one tag for our mocked class.
            scenarios.add_xml_scenario(
                scenario_name, f"Temporary scenario {temp_class.__name__}",
                "<%s/>" % temp_class.__name__
            )
            try:
                return func(*args, **kwargs)
            finally:
                scenarios.remove_scenario(scenario_name)
        return _inner
    return _decorator


class MultiViewXBlock(XBlock):
    """A bare-bone XBlock with two views."""
    def student_view(self, context=None):  # pylint: disable=W0613
        """A view, with the default name."""
        return Fragment("This is student view!")

    def another_view(self, context=None):  # pylint: disable=W0613
        """A secondary view for this block."""
        return Fragment("This is another view!")


def test_unknown_scenario():
    client = Client()

    response = client.get(reverse('scenario', args=('unknown_scenario', 'unknown_view')))
    assert response.status_code == 404


@temp_scenario(MultiViewXBlock, "multiview")
def test_multiple_views():
    client = Client()

    # The default view is student_view
    response = client.get("/view/multiview/")
    assert "This is student view!" in response.content.decode('utf-8')

    # We can ask for student_view directly
    response = client.get("/view/multiview/student_view/")
    assert "This is student view!" in response.content.decode('utf-8')

    # We can also ask for another view.
    response = client.get("/view/multiview/another_view/")
    assert "This is another view!" in response.content.decode('utf-8')


class XBlockWithHandlerAndStudentState(XBlock):
    """A bare-bone XBlock with one view and one json handler."""
    the_data = String(default="def", scope=Scope.user_state)

    def student_view(self, context=None):  # pylint: disable=W0613
        """Provide the default view."""
        body = "The data: %r." % self.the_data
        body += ":::%s:::" % self.runtime.handler_url(self, "update_the_data")
        return Fragment(body)

    @XBlock.json_handler
    def update_the_data(self, _data, suffix=''):  # pylint: disable=unused-argument
        """Mock handler that updates the student state."""
        self.the_data = self.the_data + "x"
        return {'the_data': self.the_data}


@temp_scenario(XBlockWithHandlerAndStudentState, 'testit')
def test_xblock_with_handler():
    # Tests an XBlock that provides a handler, and has some simple
    # student state
    client = Client()

    # Initially, the data is the default.
    response = client.get("/view/testit/")
    response_content = response.content.decode('utf-8')

    expected = "The data: %r." % "def"
    assert expected in response_content

    parsed = response_content.split(':::')
    assert len(parsed) == 3
    handler_url = parsed[1]

    # Now change the data.
    response = client.post(handler_url, "{}", "text/json")
    the_data = json.loads(response.content.decode('utf-8'))['the_data']
    assert the_data == "defx"

    # Change it again.
    response = client.post(handler_url, "{}", "text/json")
    the_data = json.loads(response.content.decode('utf-8'))['the_data']
    assert the_data == "defxx"


@temp_scenario(XBlock)
def test_xblock_without_handler():
    # Test that an XBlock without a handler raises an Exception
    # when we try to hit a handler on it
    client = Client()

    # Pick the most-recent usage ID just made in the temp_scenario setup...
    usage_id = ID_MANAGER.last_created_usage_id()

    # Plug that usage_id into a mock handler URL
    # /handler/[usage_id]/[handler_name]
    handler_url = reverse('handler', kwargs={
        'usage_id': usage_id,
        'handler_slug': 'does_not_exist',
        'suffix': ''
    }) + '?student=student_doesntexist'

    # The default XBlock implementation doesn't provide
    # a handler, so this call should raise an exception
    # (from xblock.runtime.Runtime.handle)
    with pytest.raises(NoSuchHandlerError):
        client.post(handler_url, '{}', 'text/json')


@temp_scenario(XBlock)
def test_xblock_invalid_handler_url():
    # Test that providing an invalid handler url will give a 404
    # when we try to hit a handler on it
    client = Client()

    handler_url = "/handler/obviously/a/fake/handler"
    result = client.post(handler_url, '{}', 'text/json')
    assert result.status_code == 404


class XBlockWithHandlers(XBlock):
    """A XBlock with one json handler."""

    def student_view(self, context=None):               # pylint: disable=W0613
        """Returned content has handler urls."""
        all_args = [
            # Arguments for handler_url
            ("send_it_back",),
            ("send_it_back", "with_some_suffix"),
            ("send_it_back", "", "a=123"),
            ("send_it_back", "", "a=123&b=456&c=789"),
            ("send_it_back", "another_suffix", "a=123&b=456&c=789"),
            ("send_it_back_public",),
            ("send_it_back_public", "with_some_suffix"),
            ("send_it_back_public", "", "a=123"),
            ("send_it_back_public", "", "a=123&b=456&c=789"),
            ("send_it_back_public", "another_suffix", "a=123&b=456&c=789"),
        ]
        urls = []
        for args in all_args:
            thirdparty = (args[0] == "send_it_back_public")
            urls.append(self.runtime.handler_url(self, *args, thirdparty=thirdparty))
        encoded = json.dumps(urls)
        return Fragment(":::" + encoded + ":::")

    def try_bad_handler_urls(self, context=None):       # pylint: disable=W0613
        """Force some assertions for the wrong kinds of handlers."""
        # A completely non-existing function name.
        with pytest.raises(ValueError, match="function name"):
            self.runtime.handler_url(self, "this_doesnt_exist")

        # An existing function, but it isn't a handler.
        with pytest.raises(ValueError, match="handler name"):
            self.runtime.handler_url(self, "try_bad_handler_urls")

        return Fragment("Everything is Fine!")

    @XBlock.handler
    def send_it_back(self, request, suffix=''):
        """Just return the data we got."""
        assert self.scope_ids.user_id == "student_1"
        response_json = json.dumps({
            'suffix': suffix,
            'a': request.GET.get('a', "no-a"),
            'b': request.GET.get('b', "no-b"),
        })
        return Response(text=str(response_json), content_type='application/json')

    @XBlock.handler
    def send_it_back_public(self, request, suffix=''):
        """Just return the data we got."""
        assert self.scope_ids.user_id == "none"
        response_json = json.dumps({
            'suffix': suffix,
            'a': request.GET.get('a', "no-a"),
            'b': request.GET.get('b', "no-b"),
        })
        return Response(text=str(response_json), content_type='application/json')


@temp_scenario(XBlockWithHandlers, 'with-handlers')
def test_xblock_with_handlers():
    # Tests of handler urls.
    client = Client()

    # The view sends a list of URLs to try.
    response = client.get("/view/with-handlers/")
    parsed = response.content.decode('utf-8').split(':::')
    assert len(parsed) == 3
    urls = json.loads(parsed[1])

    # These have to correspond to the urls in XBlockWithHandlers.student_view above.
    expecteds = [
        {'suffix': '', 'a': 'no-a', 'b': 'no-b'},
        {'suffix': 'with_some_suffix', 'a': 'no-a', 'b': 'no-b'},
        {'suffix': '', 'a': '123', 'b': 'no-b'},
        {'suffix': '', 'a': '123', 'b': '456'},
        {'suffix': 'another_suffix', 'a': '123', 'b': '456'},
        {'suffix': '', 'a': 'no-a', 'b': 'no-b'},
        {'suffix': 'with_some_suffix', 'a': 'no-a', 'b': 'no-b'},
        {'suffix': '', 'a': '123', 'b': 'no-b'},
        {'suffix': '', 'a': '123', 'b': '456'},
        {'suffix': 'another_suffix', 'a': '123', 'b': '456'},
    ]

    for url, expected in zip(urls, expecteds):
        print(url)   # so we can see which one failed, if any.
        response = client.get(url)
        assert response.status_code == 200
        actual = json.loads(response.content.decode('utf-8'))
        assert actual == expected


@temp_scenario(XBlockWithHandlers, 'with-handlers')
def test_bad_handler_urls():
    client = Client()

    response = client.get("/view/with-handlers/try_bad_handler_urls/")
    assert response.status_code == 200
    assert "Everything is Fine!" in response.content.decode('utf-8')


class XBlockWithoutStudentView(XBlock):
    """
    Test WorkbechRuntime.render caught `NoSuchViewError` exception path
    """
    the_data = String(default="def", scope=Scope.user_state)


@temp_scenario(XBlockWithoutStudentView, 'xblockwithoutstudentview')
def test_xblock_no_student_view():
    # Try to get a response. Will try to render via WorkbenchRuntime.render;
    # since no view is provided in the XBlock, will return a Fragment that
    # indicates there is no view available.
    client = Client()
    response = client.get("/view/xblockwithoutstudentview/")
    assert 'No such view' in response.content.decode('utf-8')


def test_local_resources():
    client = Client()

    # The Equality block has local resources
    result = client.get('/resource/equality_demo/public/images/correct-icon.png')
    assert result.status_code == 200
    assert result['Content-Type'] == 'image/png'

    # The Equality block defends against malicious resource URIs
    # This test has two possible ways of passing
    # 1. We return a 404.
    # 2. We raise a DisallowedFileError.
    # The code currently uses path #1 (through an overly broad
    # try/except clause). This is the right behavior in prod,
    # but horrible for debugging. It is convenient to modify
    # dev versions of xblocks to give behavior #2, since it
    # provides meaningful errors. The code below is setup to
    # support both prod and dev configurations.
    try:
        result = client.get('/resource/equality_demo/core.py')
        assert result.status_code == 404
    except DisallowedFileError:
        pass


class XBlockWithContextTracking(XBlock):
    """
    Provide a test XBlock with context tracking
    """
    registered_contexts = []

    @classmethod
    def register_context(cls, context):
        """
        Register a class-level context
        """
        cls.registered_contexts.append(context)

    @classmethod
    def clear_contexts(cls):
        """
        Clear class-level contexts
        """
        cls.registered_contexts = []

    def student_view(self, context):
        """
        Render a student view with context
        """
        self.register_context(context)
        return Fragment()


@temp_scenario(XBlockWithContextTracking, 'context_tracking')
def test_activate_id():
    client = Client()
    assert XBlockWithContextTracking.registered_contexts == []  # precondition check
    client.get("/view/context_tracking/")
    assert XBlockWithContextTracking.registered_contexts == [{'activate_block_id': None}]

    client.get("/view/context_tracking/?activate_block_id=123")
    expected = [{'activate_block_id': None}, {'activate_block_id': '123'}]
    assert XBlockWithContextTracking.registered_contexts == expected

    XBlockWithContextTracking.clear_contexts()
    client.get("/view/context_tracking/?activate_block_id=456")
    assert XBlockWithContextTracking.registered_contexts == [{'activate_block_id': '456'}]


def test_user_list():
    client = Client()
    result = client.get("/userlist/")
    assert result.status_code == 200
    assert result.content.decode('utf-8') == "[]"

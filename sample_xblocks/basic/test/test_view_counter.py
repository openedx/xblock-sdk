""" Simple test for the view counter that verifies that it is updating properly """

from __future__ import absolute_import

from six.moves import range

from mock import Mock
from sample_xblocks.basic.view_counter import ViewCounter
from xblock.runtime import DictKeyValueStore, KvsFieldData
from xblock.test.tools import TestRuntime as Runtime  # Workaround for pytest trying to collect "TestRuntime" as a test
from xblock.test.tools import assert_equals, assert_in


def test_view_counter_state():
    key_store = DictKeyValueStore()
    field_data = KvsFieldData(key_store)
    runtime = Runtime(services={'field-data': field_data})
    tester = ViewCounter(runtime, scope_ids=Mock())

    assert_equals(tester.views, 0)

    # View the XBlock five times
    for i in range(5):
        generated_html = tester.student_view({})
        # Make sure the html fragment we're expecting appears in the body_html
        assert_in('<span class="views">{0}</span>'.format(i + 1), generated_html.body_html())
        assert_equals(tester.views, i + 1)

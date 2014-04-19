""" Simple test for the view counter that verifies that it is updating properly """
from __future__ import unicode_literals
from six.moves import range

from mock import Mock

from xblock.runtime import KvsFieldData, DictKeyValueStore
from sample_xblocks.basic.view_counter import ViewCounter

from xblock.test.tools import assert_in, assert_equals


def test_view_counter_state():
    key_store = DictKeyValueStore()
    db_model = KvsFieldData(key_store)
    tester = ViewCounter(Mock(), db_model, Mock())

    assert_equals(tester.views, 0)

    # View the XBlock five times
    for i in range(5):
        generated_html = tester.student_view({})
        # Make sure the html fragment we're expecting appears in the body_html
        assert_in('<span class="views">{0}</span>'.format(i + 1), generated_html.body_html())
        assert_equals(tester.views, i + 1)

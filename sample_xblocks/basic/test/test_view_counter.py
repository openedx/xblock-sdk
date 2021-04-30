""" Simple test for the view counter that verifies that it is updating properly """



from unittest.mock import Mock
from xblock.runtime import DictKeyValueStore, KvsFieldData
from xblock.test.tools import TestRuntime as Runtime  # Workaround for pytest trying to collect "TestRuntime" as a test

from sample_xblocks.basic.view_counter import ViewCounter


def test_view_counter_state():
    key_store = DictKeyValueStore()
    field_data = KvsFieldData(key_store)
    runtime = Runtime(services={'field-data': field_data})
    tester = ViewCounter(runtime, scope_ids=Mock())

    assert tester.views == 0

    # View the XBlock five times
    for i in range(5):
        generated_html = tester.student_view({})
        # Make sure the html fragment we're expecting appears in the body_html
        assert f'<span class="views">{i + 1}</span>' in generated_html.body_html()
        assert tester.views == (i + 1)

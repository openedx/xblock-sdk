"""
Tests for workbench models.
"""

from django.test import TestCase
from xblock.fields import Scope
from xblock.runtime import KeyValueStore
from workbench.models import XBlockState


class XBlockStateTest(TestCase):
    """Tests for XBlock persistent state storage."""

    def test_parallel_writes(self):
        # Simulate what happens when multiple processes
        # update a field in parallel.
        key = KeyValueStore.Key(
            scope=Scope.parent,
            user_id="test student",
            block_scope_id="scenario.type.def",
            field_name="test field"
        )
        XBlockState.create_for_key(key)
        second = XBlockState.create_for_key(key)

        # Check that we get back the most recent state
        retrieved = XBlockState.get_for_key(key)
        self.assertEqual(retrieved.pk, second.pk)
